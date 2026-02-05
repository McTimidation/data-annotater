from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

from .forms import CSVUploadForm, RetailRowAnnotateForm
from .models import RetailRow
from .services import ingest_csv


def upload(request):

    stats = None

    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data["csv_file"]
            stats = ingest_csv(uploaded)
            form = CSVUploadForm()
    else:
        form = CSVUploadForm()

    show_all = request.GET.get("view") == "all"

    rows = RetailRow.objects.all()
    if not show_all:
        rows = rows.filter(
            Q(segment__isnull=True) | Q(retailer__isnull=True) | Q(retailer="")
        )

    rows = rows.order_by("country", "merchant", "sku")

    return render(
        request,
        "data_annotater/upload.html",
        {"form": form, "stats": stats, "rows": rows, "show_all": show_all},
    )


def retail_list(request):

    rows = (
        RetailRow.objects
        .filter(segment__isnull=True)
        .order_by("country", "merchant", "sku")
    )

    return render(request, "data_annotater/list.html", {"rows": rows})


def edit(request, pk: int):

    row = get_object_or_404(RetailRow, pk=pk)

    if request.method == "POST":
        form = RetailRowAnnotateForm(request.POST, instance=row)
        if form.is_valid():
            form.save()
            return redirect("data_annotater:upload")
    else:
        form = RetailRowAnnotateForm(instance=row)

    return render(request, "data_annotater/edit.html", {"row": row, "form": form})

