import logging, json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, Min, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _t
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta, date
from collections import OrderedDict

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from esi.decorators import token_required
from eveuniverse.models import EveType
from django.http import JsonResponse

from .models import (
    MarketTrackingConfig,
    TrackedItem,
    TrackedContract,
    MarketOrderSnapshot,
    MarketCharacter,
    TrackedStructure,
    Delivery,
    ContractSnapshot,
    ContractError,
    ContractDelivery,
)

from .utils import contract_matches
from .forms import (
    TrackedItemForm,
    DeliveryQuantityForm,
    TrackedContractForm,
    ContractDeliveryQuantityForm,
)
from .esi import get_market_history, get_type_name, get_best_prices
from .tasks import fetch_market_data, refresh_contracts

logger = logging.getLogger(__name__)

THE_FORGE = 10000002  # Jita
DOMAIN = 10000043     # Amarr
EXCLUDED_GROUP_IDS = [6, 25, 1, 14, 52, 67, 89]
EXCLUDED_CATEGORIES = ["Blueprint"]


@login_required
def item_search(request):
    q = (request.GET.get("q") or "").strip()
    page = max(int(request.GET.get("page") or 1), 1)
    page_size = 25
    offset = (page - 1) * page_size

    structure_id = request.GET.get("structure")
    taken = TrackedItem.objects.all()
    if structure_id == "global" or not structure_id:
        taken = taken.filter(structure__isnull=True)
    else:
        taken = taken.filter(structure_id=structure_id)
    taken_ids = list(taken.values_list("item_id", flat=True))

    qs = (
        EveType.objects
        .filter(published=True, name__isnull=False)
        .exclude(eve_group_id__in=EXCLUDED_GROUP_IDS)
        .exclude(eve_group__eve_category__name__in=EXCLUDED_CATEGORIES)
    )

    if q:
        qs = qs.filter(name__icontains=q)

    qs = (
        qs.exclude(id__in=taken_ids)
          .only("id", "name")
          .order_by("name")
    )

    total = qs.count()
    items = list(qs[offset: offset + page_size].values("id", "name"))

    results = [{"id": it["id"], "text": it["name"]} for it in items]
    return JsonResponse({
        "results": results,
        "pagination": {"more": (offset + page_size) < total}
    })


class ItemPriceDetailView(TemplateView):
    template_name = "markettracker/item_detail.html"

    def get_context_data(self, type_id: int, **kwargs):
        import json
        import logging
        from collections import OrderedDict
        from datetime import timedelta, date
        from django.core.cache import cache
        from django.utils import timezone

        logger = logging.getLogger(__name__)

        ctx = super().get_context_data(**kwargs)
        type_id = int(type_id)

        # --- Item name & icon (cache) ---
        cache_key_name = f"mt:typename:{type_id}"
        item_name = cache.get(cache_key_name)
        if not item_name or isinstance(item_name, dict):
            # get_type_name masz już zaimportowane na górze pliku
            item_name = get_type_name(type_id) or f"Type {type_id}"
            cache.set(cache_key_name, item_name, 3600)
        item_icon = f"https://images.evetech.net/types/{type_id}/icon?size=64"

        # --- Market history (cache 10 min) ---
        key_f = f"mt:hist:{THE_FORGE}:{type_id}"
        key_d = f"mt:hist:{DOMAIN}:{type_id}"
        data_f = cache.get(key_f)
        data_d = cache.get(key_d)

        def _safe_fetch(region_id, cache_key):
            data = cache.get(cache_key)
            err = None
            if data is None:
                try:
                    data = get_market_history(region_id, type_id)
                except Exception as e:
                    data = []
                    err = str(e)
                cache.set(cache_key, data, 600)
            return data, err

        data_f, err_f = _safe_fetch(THE_FORGE, key_f) if data_f is None else (data_f, None)
        data_d, err_d = _safe_fetch(DOMAIN, key_d)    if data_d is None else (data_d, None)

        cutoff = timezone.now().date() - timedelta(days=30)

        def to_map(rows):
            """Zwraca OrderedDict {'YYYY-MM-DD': float(average)} posortowany po dacie rosnąco."""
            m = {}
            for r in rows or []:
                ds = r.get("date")
                avg = r.get("average")
                if not ds or avg is None:
                    continue
                try:
                    date.fromisoformat(ds)
                except ValueError:
                    continue
                m[ds] = float(avg)
            return OrderedDict(sorted(m.items(), key=lambda kv: kv[0]))

        map_f = to_map(data_f)
        map_d = to_map(data_d)

        # wspólne etykiety (ostatnie 30 dni; jeżeli pusto po cięciu, bierzemy ostatnie do 30)
        all_dates = sorted(set(map_f.keys()) | set(map_d.keys()))
        last_30 = [ds for ds in all_dates if date.fromisoformat(ds) >= cutoff]
        if not last_30:
            last_30 = all_dates[-30:]
        else:
            last_30 = last_30[-30:]

        labels = last_30
        series_f = [map_f.get(ds, None) for ds in labels]
        series_d = [map_d.get(ds, None) for ds in labels]

        # --- BEST PRICES (live + fallback z historii) ---
        def best_from_orders(region_id: int):
            key = f"mt:best:v2:{region_id}:{type_id}"
            cached = cache.get(key)
            if cached is not None:
                return cached  # {"sell": x|None, "buy": y|None}
            try:
                # get_best_prices masz już zaimportowane na górze pliku
                out = get_best_prices(region_id, type_id)
            except Exception:
                logger.exception("get_best_prices failed (region=%s type_id=%s)", region_id, type_id)
                out = {"sell": None, "buy": None}
            cache.set(key, out, 60)  # 1 minuta
            return out

        def last_hist_extrema(rows: list[dict]) -> tuple[float | None, float | None]:
            """Zwraca (sell≈lowest, buy≈highest) dla NAJNOWSZEGO dnia w historii."""
            if not rows:
                return None, None
            try:
                last = max(rows, key=lambda r: r.get("date", ""))
            except Exception:
                last = rows[-1]
            lo = last.get("lowest")
            hi = last.get("highest")
            return (float(lo) if lo is not None else None,
                    float(hi) if hi is not None else None)

        # live z orders
        live_f = best_from_orders(THE_FORGE)   # {"sell":..., "buy":...}
        live_d = best_from_orders(DOMAIN)

        # fallback z historii (ostatni dzień)
        hist_sell_f, hist_buy_f = last_hist_extrema(data_f or [])
        hist_sell_d, hist_buy_d = last_hist_extrema(data_d or [])

        # wybór: live -> hist -> None + znacznik źródła
        def pick(live_val, hist_val):
            if live_val is not None:
                return live_val, "live"
            if hist_val is not None:
                return hist_val, "hist"
            return None, None

        forge_best_sell, forge_best_src_s = pick(live_f.get("sell"), hist_sell_f)
        forge_best_buy,  forge_best_src_b = pick(live_f.get("buy"),  hist_buy_f)
        domain_best_sell, domain_best_src_s = pick(live_d.get("sell"), hist_sell_d)
        domain_best_buy,  domain_best_src_b = pick(live_d.get("buy"),  hist_buy_d)
        forge_best_src = forge_best_src_s or forge_best_src_b
        domain_best_src = domain_best_src_s or domain_best_src_b

        logger.debug(
            "Best Jita: sell=%s buy=%s src=%s | Best Amarr: sell=%s buy=%s src=%s",
            forge_best_sell, forge_best_buy, forge_best_src,
            domain_best_sell, domain_best_buy, domain_best_src
        )

        # --- Context ---
        ctx.update({
            "type_id": type_id,
            "item_name": item_name,
            "item_icon": item_icon,

            "labels_json": json.dumps(labels),
            "forge_json": json.dumps(series_f),
            "domain_json": json.dumps(series_d),

            "region_name_f": "Jita (The Forge)",
            "region_name_d": "Amarr (Domain)",

            "has_data_f": any(v is not None for v in series_f),
            "has_data_d": any(v is not None for v in series_d),

            "forge_best_sell": forge_best_sell,
            "forge_best_buy":  forge_best_buy,
            "forge_best_src":  forge_best_src,   # "live" / "hist" / None

            "domain_best_sell": domain_best_sell,
            "domain_best_buy":  domain_best_buy,
            "domain_best_src":  domain_best_src,

            "diag": {
                "labels_len": len(labels),
                "forge_non_null": sum(1 for v in series_f if v is not None),
                "domain_non_null": sum(1 for v in series_d if v is not None),
                "forge_raw": len(data_f or []),
                "domain_raw": len(data_d or []),
                "forge_sample": (data_f[-1] if isinstance(data_f, list) and data_f else None),
                "domain_sample": (data_d[-1] if isinstance(data_d, list) and data_d else None),
                "forge_err": err_f,
                "domain_err": err_d,
            }
        })
        return ctx



@login_required
@token_required(scopes=[
    "esi-contracts.read_character_contracts.v1",
    "esi-assets.read_assets.v1",
    "esi-markets.read_character_orders.v1"
])
def character_login_list(request, token):
    if MarketCharacter.objects.filter(token=token).exists():
        messages.error(request, _t("This character is already used as admin market character."))
        return redirect("markettracker:list_items")

    messages.success(request, _t("Character successfully linked for item list tracking."))
    return redirect("markettracker:list_items")


@login_required
@token_required(scopes=[
    "esi-markets.structure_markets.v1",
    "esi-universe.read_structures.v1",
    "esi-contracts.read_character_contracts.v1",
    "esi-assets.read_assets.v1",
    "esi-markets.read_character_orders.v1"
])
def character_login_manage(request, token):
    MarketCharacter.objects.all().delete()

    eve_character, _ = EveCharacter.objects.get_or_create(
        character_id=token.character_id, defaults={"character_name": token.character_name}
    )
    ownership, _ = CharacterOwnership.objects.get_or_create(character=eve_character, user=request.user)
    MarketCharacter.objects.create(character=ownership, token=token)

    messages.success(request, _t("Admin market character successfully linked."))
    return redirect("markettracker:manage_stock")


@login_required
def list_items_view(request):
    config = MarketTrackingConfig.objects.first()
    if not config:
        messages.error(request, _t("Market tracking configuration not found."))
        return redirect("markettracker:manage_stock")

    # nazwa lokalizacji (region albo znana struktura)
    location_name = str(config.location_id)
    if config.scope == "region":
        from eveuniverse.models import EveRegion
        try:
            location_name = EveRegion.objects.get(id=config.location_id).name
        except EveRegion.DoesNotExist:
            pass
    else:
        try:
            structure = TrackedStructure.objects.get(structure_id=config.location_id)
            location_name = structure.name
        except TrackedStructure.DoesNotExist:
            pass

    # progi – bierzemy z configu
    yellow_threshold = config.yellow_threshold or 50
    red_threshold = config.red_threshold or 25

    q = request.GET.get("q", "").strip()
    status_filter = (request.GET.get("status") or "").lower()  # 'red' jako toggle

    tracked_items = TrackedItem.objects.all()
    if q:
        tracked_items = tracked_items.filter(item__name__icontains=q)

    items_data = []
    for tracked in tracked_items:
        orders = MarketOrderSnapshot.objects.filter(tracked_item=tracked)
        agg = orders.aggregate(min_price=Min("price"), total_vol=Sum("volume_remain"))
        min_price = agg["min_price"]
        total_volume = agg["total_vol"] or 0

        desired = tracked.desired_quantity or 1
        percentage = int((total_volume / desired) * 100)

        if percentage <= red_threshold:
            computed_status = "RED"
        elif percentage <= yellow_threshold:
            computed_status = "YELLOW"
        else:
            computed_status = "OK"

        items_data.append({
            "item": tracked.item,
            "desired_quantity": tracked.desired_quantity,
            "price": min_price,
            "volume_remain": total_volume,
            "status": computed_status,
            "percentage": percentage,
        })

    # filtr toggle "Only RED"
    if status_filter == "red":
        items_data = [it for it in items_data if it["status"] == "RED"]
    if status_filter == "yellow":
        items_data = [it for it in items_data if it["status"] == "YELLOW"]

    return render(
        request,
        "markettracker/list_items.html",
        {
            "items": items_data,
            "region": location_name,
            "q": q,
            "status": status_filter,
            "yellow_threshold": yellow_threshold,
            "red_threshold": red_threshold,
        },
    )


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def manage_stock_view(request):
    """
    Jeden widok obsługuje:
    - Items: add/edit
    - Contracts: add/edit
    - Szybkie refresh'e: items / contracts
    """
    q = request.GET.get("q", "")
    cq = request.GET.get("cq", "")

    add_mode = "add" in request.GET
    edit_id = request.GET.get("edit_id")

    tc_add_mode = "tc_add" in request.GET
    tc_edit_id = request.GET.get("tc_edit")

    if request.method == "POST":
        if "refresh" in request.POST:
            fetch_market_data.delay(request.user.pk)
            messages.success(request, _t("Market data refresh started."))
            return redirect("markettracker:manage_stock")

        if "refresh_contracts" in request.POST:
            refresh_contracts.delay()
            messages.success(request, _t("Contracts refresh started."))
            return redirect("markettracker:manage_stock")

        if "add" in request.POST:
            form = TrackedItemForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _t("Item added successfully."))
                return redirect("markettracker:manage_stock")

        if "edit" in request.POST:
            tracked_item = get_object_or_404(TrackedItem, pk=request.POST.get("item_id"))
            form = TrackedItemForm(request.POST, instance=tracked_item)
            if form.is_valid():
                form.save()
                messages.success(request, _t("Item updated successfully."))
                return redirect("markettracker:manage_stock")

        if "tc_add_submit" in request.POST:
            tc_form = TrackedContractForm(request.POST)
            if tc_form.is_valid():
                obj = tc_form.save(commit=False)
                obj.created_by = request.user
                obj.save()
                messages.success(request, _t("Tracked contract added."))
                return redirect("markettracker:manage_stock")
            form = None
            tc_add_mode = True  # pokaż ponownie formularz kontraktu

        if "tc_edit_submit" in request.POST:
            tc_obj = get_object_or_404(TrackedContract, pk=request.POST.get("tc_id"))
            tc_form = TrackedContractForm(request.POST, instance=tc_obj)
            if tc_form.is_valid():
                tc_form.save()
                messages.success(request, _t("Tracked contract updated."))
                return redirect("markettracker:manage_stock")
            tc_edit_id = tc_obj.pk

    # GET – przygotowanie formularzy
    if edit_id:
        _obj = get_object_or_404(TrackedItem, pk=edit_id)
        form = TrackedItemForm(instance=_obj)
    elif add_mode:
        form = TrackedItemForm()
    else:
        form = None

    tc_form = None
    if tc_add_mode:
        tc_form = TrackedContractForm()
    elif tc_edit_id:
        _tc = get_object_or_404(TrackedContract, pk=tc_edit_id)
        tc_form = TrackedContractForm(instance=_tc)

    # ⬇️ KLUCZ: jeżeli pokazujemy któryś formularz, zwracamy lekki kontekst
    if form is not None or tc_form is not None:
        market_character = MarketCharacter.objects.first()
        return render(
            request,
            "markettracker/manage_stock.html",
            {
                "form": form,
                "tc_form": tc_form,
                "tc_add_mode": tc_add_mode,
                "tc_edit_id": tc_edit_id,
                "market_character": market_character,
                # NIE wysyłamy tu tracked_items / tracked_contracts — oszczędzamy czas
            },
        )

    # ⬇️ Zwykły „panel” — dopiero tu licz cięższe listy (też w miarę oszczędnie)
    tracked_items = TrackedItem.objects.select_related("item").all()
    if q:
        tracked_items = tracked_items.filter(item__name__icontains=q)

    tracked_contracts = (
        TrackedContract.objects
        .select_related("fitting", "fitting__ship_type")
        .only(
            "id", "mode", "title_filter", "desired_quantity", "max_price",
            "fitting__id", "fitting__name", "fitting__ship_type__name"
        )
        .order_by("mode", "title_filter", "fitting__name")
    )
    if cq:
        tracked_contracts = tracked_contracts.filter(
            Q(fitting__ship_type__name__icontains=cq) |
            Q(fitting__name__icontains=cq) |
            Q(title_filter__icontains=cq)
        )

    market_character = MarketCharacter.objects.first()

    return render(
        request,
        "markettracker/manage_stock.html",
        {
            "form": None,
            "tc_form": None,
            "tc_add_mode": False,
            "tc_edit_id": None,
            "tracked_items": tracked_items,
            "tracked_contracts": tracked_contracts,
            "market_character": market_character,
            "q": q,
            "cq": cq,
        },
    )



@login_required
def refresh_market_data(request):
    fetch_market_data.delay(request.user.pk)
    messages.success(request, _t("Market data refresh started."))
    return redirect("markettracker:manage_stock")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def contract_errors_view(request):
    errors = ContractError.objects.filter(is_resolved=False).order_by("-created_at")
    return render(request, "markettracker/contract_errors.html", {"errors": errors})


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
@require_POST
def delete_trackeditem(request, pk):
    item = get_object_or_404(TrackedItem, pk=pk)
    item.delete()
    messages.success(request, _t("Item deleted successfully."))
    return redirect("markettracker:manage_stock")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def tracked_contract_delete(request, pk):
    if request.method != "POST":
        messages.error(request, _t("Invalid request."))
        return redirect("markettracker:manage_stock")
    tc = get_object_or_404(TrackedContract, pk=pk)
    tc.delete()
    messages.success(request, _t("Tracked contract deleted."))
    return redirect("markettracker:manage_stock")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def tracked_contract_edit(request, pk):
    url = f"{reverse('markettracker:manage_stock')}?tc_edit={pk}"
    return redirect(url)


@login_required
def create_delivery(request, item_id):
    tracked_item = get_object_or_404(TrackedItem, item__id=item_id)

    if request.method == "POST":
        form = DeliveryQuantityForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.user = request.user
            delivery.item = tracked_item.item
            delivery.save()
            messages.success(request, _t("Delivery declared successfully."))
            return redirect("markettracker:deliveries_list")
    else:
        form = DeliveryQuantityForm()

    return render(request, "markettracker/delivery_form.html", {"form": form, "tracked_item": tracked_item})


@login_required
def create_contract_delivery(request, tc_id):
    tc = get_object_or_404(TrackedContract, pk=tc_id)
    if request.method == "POST":
        form = ContractDeliveryQuantityForm(request.POST)
        if form.is_valid():
            d = form.save(commit=False)
            d.user = request.user
            d.tracked_contract = tc
            d.save()
            messages.success(request, _t("Contract delivery declared."))
            return redirect("markettracker:deliveries_list")
    else:
        form = ContractDeliveryQuantityForm()
    return render(request, "markettracker/contract_delivery_form.html", {"form": form, "tc": tc})


@login_required
def deliveries_list_view(request):
    item_deliveries = Delivery.objects.filter(user=request.user, status="PENDING")
    contract_deliveries = ContractDelivery.objects.filter(user=request.user, status="PENDING").select_related(
        "tracked_contract", "tracked_contract__fitting"
    )
    return render(request, "markettracker/deliveries_list.html", {
        "item_deliveries": item_deliveries,
        "contract_deliveries": contract_deliveries,
    })


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def admin_deliveries_view(request):
    item_deliveries = Delivery.objects.all()
    contract_deliveries = ContractDelivery.objects.all().select_related(
        "tracked_contract", "tracked_contract__fitting", "user"
    )
    return render(request, "markettracker/admin_deliveries.html", {
        "item_deliveries": item_deliveries,
        "contract_deliveries": contract_deliveries,
    })


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def delete_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.delete()
    messages.success(request, _t("Delivery deleted successfully."))
    return redirect("markettracker:admin_deliveries")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def finish_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    delivery.delivered_quantity = delivery.declared_quantity
    delivery.status = "FINISHED"
    delivery.save()
    messages.success(request, _t("Delivery marked as finished."))
    return redirect("markettracker:admin_deliveries")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def refresh_contracts_data(request):
    refresh_contracts.delay()
    messages.success(request, _t("Contracts refresh started."))
    return redirect("markettracker:contracts_list")


@login_required
@permission_required("markettracker.basic_access", raise_exception=True)
def contracts_list_view(request):
    alert = MarketTrackingConfig.objects.first()
    yellow = alert.yellow_threshold if alert else 50
    red = alert.red_threshold if alert else 25

    tc_query = (request.GET.get("tc") or "").strip().lower()
    status_filter = (request.GET.get("status") or "").lower()

    all_contracts = list(
        ContractSnapshot.objects
        .filter(status__iexact="outstanding", type__iexact="item_exchange")
        .order_by("-date_issued")
    )

    tracked_qs = (
        TrackedContract.objects
        .select_related("fitting", "fitting__ship_type")
        .all()
    )

    rows = []
    for tc in tracked_qs:
        matched = []
        for c in all_contracts:
            ok, reason = contract_matches(tc, c)
            if ok:
                matched.append(c)
            else:
                logger.debug("[Contracts] No match for TC#%s vs #%s: %s", tc.id, c.contract_id, reason)

        current_qty = len(matched)
        desired = tc.desired_quantity or 0

        if desired <= 0:
            status = "OK"
            percent = 100
        else:
            percent = int((current_qty / desired) * 100)
            if percent <= red:
                status = "RED"
            elif percent <= yellow:
                status = "YELLOW"
            else:
                status = "OK"

        min_price = None
        if matched:
            prices = [float(m.price) for m in matched if getattr(m, "price", None) is not None]
            if prices:
                min_price = min(prices)

        if tc.mode == TrackedContract.Mode.DOCTRINE and tc.fitting:
            icon_type_id = tc.fitting.ship_type_id
            name = tc.fitting.name
            ship_name = getattr(tc.fitting.ship_type, "name", "") or ""
        else:
            icon_type_id = None
            name = tc.title_filter or "—"
            ship_name = ""

        rows.append({
            "tc": tc,
            "mode": tc.mode,
            "name": name,
            "ship_name": ship_name,
            "icon_type_id": icon_type_id,
            "current_qty": current_qty,
            "desired_qty": desired,
            "min_price": min_price,
            "status": status,
            "percent": percent,
        })
    if tc_query:
        def _hit(r):
            hay = " ".join([
                r["name"] or "",
                r.get("ship_name") or "",
                getattr(r["tc"], "title_filter", "") or "",
            ]).lower()
            return tc_query in hay
        rows = [r for r in rows if _hit(r)]

    if status_filter == "red":
        rows = [r for r in rows if r["status"] == "RED"]
    elif status_filter == "yellow":
        rows = [r for r in rows if r["status"] == "YELLOW"]

    return render(
        request,
        "markettracker/contracts_list.html",
        {
            "rows": rows,
            "tc": request.GET.get("tc", ""),
            "status": status_filter,
            "yellow_threshold": yellow,
            "red_threshold": red,
        },
    )
