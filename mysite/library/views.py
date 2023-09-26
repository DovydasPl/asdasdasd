from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django.urls import reverse
from .models import Book, BookInstance, Author, Profile
from .forms import BookReviewForm, UserUpdateForm, ProfileUpdateForm


def index(request):
    profiles = Profile.objects.all()
    book_count = Book.objects.all().count()
    book_instance_count = BookInstance.objects.all().count()
    author_count = Author.objects.all().count()
    available_book_instance_count = BookInstance.objects.filter(
        status='g').count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    zodynas = {
        'profiliai': profiles,
        'knygu_skaicius': book_count,
        'knygu_kopiju_skaicius': book_instance_count,
        'autoriu_skaicius': author_count,
        'galimu_paimti_knygu_kopiju_skaicius': available_book_instance_count,
        'zodis': 'Labas',
        'num_visits': num_visits
    }

    return render(request, 'index.html', context=zodynas)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profilis)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profilis)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile.html', context=context)


@csrf_protect
def register(request):
    if request.method == "POST":
        # pasiimame reikšmes iš registracijos formos
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        # tikriname, ar sutampa slaptažodžiai
        if password == password2:
            # tikriname, ar neužimtas username
            if User.objects.filter(username=username).exists():
                messages.error(
                    request, f'Vartotojo vardas {username} užimtas!')
                return redirect('register')
            else:
                # tikriname, ar nėra tokio pat email
                if User.objects.filter(email=email).exists():
                    messages.error(
                        request, f'Vartotojas su el. paštu {email} jau užregistruotas!')
                    return redirect('register')
                else:
                    # jeigu viskas tvarkoje, sukuriame naują vartotoją
                    User.objects.create_user(
                        username=username, email=email, password=password)
                    messages.info(
                        request, f'Vartotojas {username} užregistruotas!')
                    return redirect('login')
        else:
            messages.error(request, 'Slaptažodžiai nesutampa!')
            return redirect('register')
    return render(request, 'register.html')


@login_required
def authors(request):
    paginator = Paginator(Author.objects.all(), 2)
    page_number = request.GET.get('page')
    authors = paginator.get_page(page_number)

    context = {
        'authors': authors
    }

    return render(request, 'authors.html', context=context)


def author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)
    context = {
        'author': author
    }
    return render(request, 'author.html', context=context)


def search(request):
    # gausim paieskos reiksme is urlo
    query = request.GET.get('query')
    # pagal paieskos reiksme prafiltruosim knygas
    search_results = Book.objects.filter(
        Q(title__icontains=query) | Q(summary__icontains=query))
    # atidarysim puslapi su rastom knygom
    context = {
        'books': search_results,
        'query': query
    }
    return render(request, 'search.html', context=context)


class BookListView(generic.ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'book_list'
    queryset = Book.objects.all()
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['data'] = 'random text'
        return context


class BookDetailView(FormMixin, generic.DetailView):
    model = Book
    template_name = 'book_detail.html'
    form_class = BookReviewForm

    # nurodome, kur atsidursime komentaro sėkmės atveju.
    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.id})

    # standartinis post metodo perrašymas, naudojant FormMixin, galite kopijuoti tiesiai į savo projektą.
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # štai čia nurodome, kad knyga bus būtent ta, po kuria komentuojame, o vartotojas bus tas, kuris yra prisijungęs.
    def form_valid(self, form):
        form.instance.book = self.object
        form.instance.reviewer = self.request.user
        form.save()
        return super(BookDetailView, self).form_valid(form)


class TakenBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'user_books.html'
    context_object_name = 'taken_books'

    def get_queryset(self):
        return BookInstance.objects.filter(reader=self.request.user).filter(status='p')


@login_required
def taken_books(request):
    books = BookInstance.objects.filter(reader=request.user).filter(status='p')

    context = {
        'taken_books': books
    }

    return render(request, 'user_books.html', context=context)


class TakenBooksByUserDetailView(LoginRequiredMixin, generic.DetailView):
    model = BookInstance
    template_name = 'user_book.html'
    context_object_name = 'taken_book'


class TakenBooksByUserCreateView(LoginRequiredMixin, generic.CreateView):
    model = BookInstance
    template_name = 'user_book_new.html'
    success_url = '/library/my-books/'
    fields = ['book']

    def form_valid(self, form):
        # prie formos pridedam trukstamas reiksmes
        form.instance.reader = self.request.user
        form.instance.status = 'p'
        form.instance.due_back = '2024-11-11'
        return super().form_valid(form)


class TakenBooksByUserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = BookInstance
    success_url = '/library/my-books/'
    template_name = 'user_book_delete.html'
    context_object_name = 'taken_book'
