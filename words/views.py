from django.shortcuts import render, redirect, reverse
from django.core.serializers import serialize
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView


from .models import Card, Deck
from memorisation.models import Practice
from account.decorators import teacher_required, student_required


@method_decorator([login_required, student_required], name='dispatch')
class DeckCreateView(CreateView):
    model = Deck
    fields = ('category', 'color',)
    template_name = 'words/deck_add.html'

    def form_valid(self, form):
        deck = form.save(commit=False)
        deck.student = self.request.user.student
        deck.save()
        messages.success(self.request, "Deck created!")
        return redirect('account:dashboard')


@method_decorator([login_required, student_required], name='dispatch')
class DeckListView(ListView):
    model = Deck
    template_name = 'words/deck_list.html'

    def get_queryset(self):
        queryset = Deck.objects.filter(student=self.request.user.student)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class CardListView(ListView):
    model = Card
    template_name = 'words/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        deck_id = self.kwargs['pk']
        queryset = Card.objects.filter(deck_id=deck_id)
        return queryset


@method_decorator([login_required], name='dispatch')
class CardCreateView(CreateView):
    model = Card
    fields = '__all__'
    template_name = 'words/card_add.html'

    def form_valid(self, form):
        card = form.save(commit=False)
        card.save()
        practice = Practice(card=card, student=self.request.user.student)
        practice.save()

        messages.success(self.request, "Card created!")
        return redirect('account:dashboard')


@method_decorator([login_required, student_required], name='dispatch')
class DeckUpdateView(UpdateView):
    model = Deck
    fields = ('category', 'color', )
    context_object_name = 'deck'
    template_name = 'words/deck_update.html'

    def get_queryset(self):
        return self.request.user.student.decks.all()

    def get_success_url(self):
        return reverse('words:deck_update', kwargs={'pk': self.object.pk})


@method_decorator([login_required, student_required], name='dispatch')
class CardUpdateView(UpdateView):
    model = Card
    fields = ('word', 'explanation', 'translation',  'synonymes')
    context_object_name = 'card'
    template_name = 'words/card_update.html'

    def get_queryset(self):
        queryset = Card.objects.filter(pk=self.kwargs['pk'])
        return queryset

    def get_success_url(self):
        return reverse('words:card_update', kwargs={'pk': self.object.pk})


@method_decorator([login_required, student_required], name='dispatch')
class CardDeleteView(DeleteView):
    model = Card
    context_object_name = 'card'
    template_name = 'words/card_delete_confirm.html'
    pk_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        card = self.get_object()
        messages.success(
            request, 'The card %s was deleted with success!' % card.word)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Card.objects.filter(pk=self.kwargs['pk'])
        return queryset

    def get_success_url(self):
        return reverse('words:deck_list')


@method_decorator([login_required, student_required], name='dispatch')
class DeckDeleteView(DeleteView):
    model = Deck
    context_object_name = 'deck'
    template_name = 'words/deck_delete_confirm.html'
    pk_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        deck = self.get_object()
        messages.success(
            request, 'The deck %s was deleted with success!' % deck.category)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Deck.objects.filter(pk=self.kwargs['pk'])
        return queryset

    def get_success_url(self):
        return reverse('words:deck_list')


@login_required
def cards(request):
    queryset = Card.objects.filter(deck__student__user=request.user)
    queryset = serialize('json', queryset)
    return HttpResponse(queryset, content_type="application/json")


@login_required
@student_required
def fetch_cards(request):
    return render(request, 'games/fetch_test.html')
