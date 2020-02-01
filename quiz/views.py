from django import forms
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.db.models import Count


from account.decorators import teacher_required
from .models import Quiz
from .forms import QuestionForm


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name',)
    template_name = 'quiz/add_quiz.html'

    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(
            self.request, 'The quiz was created with success! Go ahead and add some questions now.')
        return redirect('account:dashboard')


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'quiz/quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .annotate(questions_count=Count('questions', distinct=True))
        return queryset


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', )
    context_object_name = 'quiz'
    template_name = 'quiz/quiz_update.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(
            answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz:quiz_update', kwargs={'pk': self.object.pk})


@method_decorator([login_required, teacher_required], name='dispatch')
class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'quiz/quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz:quiz_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(
            request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


@login_required
@teacher_required
def question_add(request, pk):

    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(
                request, 'You may now add answers/options to the question.')
            return redirect('quiz:quiz_list', )
            # quiz.pk, question.pk
    else:
        form = QuestionForm()

    return render(request, 'quiz/question_add.html', {'quiz': quiz, 'form': form})
