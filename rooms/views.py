from django.http import Http404
from django.views.generic import (
    ListView,
    DetailView,
    View,
    UpdateView,
    FormView,
)
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin

from users import mixins as user_mixins
from . import models, forms


class HomeView(ListView):

    """HomeView Definition"""

    model = models.Room
    paginate_by = 12
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


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):

    model = models.Room
    form_class = forms.RoomUpdateForm
    template_name = "rooms/room_edit.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


class RoomPhotosView(user_mixins.LoggedInOnlyView, DetailView):
    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "사진을 지울 수 없습니다")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "사진이 삭제됐습니다")
        return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    model = models.Photo
    template_name = "rooms/photo_edit.html"
    fields = ("caption",)
    pk_url_kwarg = "photo_pk"
    success_message = "사진이 업데이트 되었습니다"

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(user_mixins.LoggedInOnlyView, FormView):
    form_class = forms.CreatePhotoForm
    template_name = "rooms/photo_create.html"

    def form_valid(self, form):
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "사진이 업로드 되었습니디")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))


class CreateRoomView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form):
        room = form.save()
        room.host = self.request.user
        room.save()
        form.save_m2m()
        messages.success(self.request, "Room Uploaded")
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))
