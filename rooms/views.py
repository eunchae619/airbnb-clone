from django.views.generic import ListView, DetailView, View
from django.shortcuts import render
from django.core.paginator import Paginator
from . import models, forms


class HomeView(ListView):

    """HomeView Definition"""

    model = models.Room
    paginate_by = 10
    ordering = "created"
    paginate_orphans = 5
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RoomDetail(DetailView):

    """RoomDetail Definition"""

    model = models.Room


class SearchView(View):

    """ SearchView Definition """

    def get(self, request):

        country = request.GET.get("country")
        city = request.GET.get("city")

        if country:

            form = forms.SearchForm(request.GET)

            if form.is_valid():

                city = form.cleaned_data.get("city")
                country = form.cleaned_data.get("country")
                room_type = form.cleaned_data.get("room_type")
                price = form.cleaned_data.get("price")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guests__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["host__superhost"] = True

                qs = models.Room.objects.filter(**filter_args)

                for amenity in amenities:
                    qs = qs.filter(amenities=amenity)

                for facility in facilities:
                    qs = qs.filter(facilities=facility)

                qs = qs.order_by("-created")

                paginator = Paginator(qs, 10, orphans=5)

                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)
                full_page = request.get_full_path()
                previous_page = ""
                next_page = ""

                if "page" in full_page:
                    previous_page = full_page.replace(
                        f"page={rooms.number}", f"page={rooms.number -1}"
                    )
                    next_page = full_page.replace(
                        f"page={rooms.number}", f"page={rooms.number +1}"
                    )
                else:
                    previous_page = f"{full_page}&page={rooms.number -1}"
                    next_page = f"{full_page}&page={rooms.number +1}"

        else:
            city = request.GET.get("city")
            city = str.capitalize(city)
            if len(city) == 0:
                city = "Anywhere"

            if city == "Anywhere":
                form = forms.SearchForm()
                qs = models.Room.objects.all()
            else:
                form = forms.SearchForm({"city": city, "country": "KR"})
                qs = models.Room.objects.filter(city__startswith=city).order_by(
                    "-created"
                )

            paginator = Paginator(qs, 10, orphans=5)

            page = request.GET.get("page", 1)

            rooms = paginator.get_page(page)
            full_page = request.get_full_path()
            previous_page = ""
            next_page = ""

            if "page" in full_page:
                previous_page = full_page.replace(
                    f"page={rooms.number}", f"page={rooms.number -1}"
                )
                next_page = full_page.replace(
                    f"page={rooms.number}", f"page={rooms.number +1}"
                )
            else:
                previous_page = f"{full_page}&page={rooms.number -1}"
                next_page = f"{full_page}&page={rooms.number +1}"

        return render(
            request,
            "rooms/search.html",
            {
                "form": form,
                "rooms": rooms,
                "previous_page": previous_page,
                "next_page": next_page,
            },
        )