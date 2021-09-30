
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Poll, Choice, Vote
from .forms import PollAddForm, EditPollForm, ChoiceAddForm



def home(request):
    return render(request,'home.html')



def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'home')
            return redirect(redirect_url)
        else:
            messages.error(request, "Username Or Password is incorrect!!",
                           extra_tags='alert alert-warning alert-dismissible fade show')

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('/home/')


def create_user(request):
    if request.method == 'POST':
        check1 = False
        check2 = False
        check3 = False
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            email = form.cleaned_data['email']

            if password1 != password2:
                check1 = True
                messages.error(request, 'Password doesn\'t matched',
                               extra_tags='alert alert-warning alert-dismissible fade show')
            if User.objects.filter(username=username).exists():
                check2 = True
                messages.error(request, 'Username already exists',
                               extra_tags='alert alert-warning alert-dismissible fade show')
            if User.objects.filter(email=email).exists():
                check3 = True
                messages.error(request, 'Email already registered',
                               extra_tags='alert alert-warning alert-dismissible fade show')

            if check1 or check2 or check3:
                messages.error(
                    request, "Registration Failed", extra_tags='alert alert-warning alert-dismissible fade show')
                return redirect('register')
            else:
                user = User.objects.create_user(
                    username=username, password=password1, email=email)
                messages.success(
                    request, f'Thanks for registering {user.username}!', extra_tags='alert alert-success alert-dismissible fade show')
                return redirect('/login/')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})




@login_required()
def polls_list(request):
    all_polls = Poll.objects.all()
    search_term = ''
    if 'name' in request.GET:
        all_polls = all_polls.order_by('text')

    if 'date' in request.GET:
        all_polls = all_polls.order_by('pub_date')

    if 'vote' in request.GET:
        all_polls = all_polls.annotate(Count('vote')).order_by('vote__count')

    if 'search' in request.GET:
        search_term = request.GET['search']
        all_polls = all_polls.filter(text__icontains=search_term)

    paginator = Paginator(all_polls, 6)  # Show 6 contacts per page
    page = request.GET.get('page')
    polls = paginator.get_page(page)

    get_dict_copy = request.GET.copy()
    params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()
    print(params)
    context = {
        'polls': polls,
        'params': params,
        'search_term': search_term,
    }
    return render(request, 'polls_list.html', context)


@login_required()
def list_by_user(request):
    all_polls = Poll.objects.filter(owner=request.user)
    paginator = Paginator(all_polls, 7)  # Show 7 contacts per page

    page = request.GET.get('page')
    polls = paginator.get_page(page)

    context = {
        'polls': polls,
    }
    return render(request, 'polls_list.html', context)


@login_required()
def polls_add(request):
    if request.user.has_perm('add_poll'):
        if request.method == 'POST':
            form = PollAddForm(request.POST)
            if form.is_valid:
                poll = form.save(commit=False)
                poll.owner = request.user
                poll.save()
                new_choice1 = Choice(
                    poll=poll, choice_text=form.cleaned_data['choice1']).save()
                new_choice2 = Choice(
                    poll=poll, choice_text=form.cleaned_data['choice2']).save()

                messages.success(
                    request, "Poll & Choices added successfully", extra_tags='alert alert-success alert-dismissible fade show')

                return redirect('/list/')
        else:
            form = PollAddForm()
        context = {
            'form': form,
        }
        return render(request, 'add_poll.html', context)
    else:
        return HttpResponse("Sorry but you don't have permission to do that!")


@login_required
def polls_edit(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('/home/')

    if request.method == 'POST':
        form = EditPollForm(request.POST, instance=poll)
        if form.is_valid:
            form.save()
            messages.success(request, "Poll Updated successfully",
                             extra_tags='alert alert-success alert-dismissible fade show')
            return redirect("/list/")

    else:
        form = EditPollForm(instance=poll)

    return render(request, "poll_edit.html", {'form': form, 'poll': poll})


@login_required
def polls_delete(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('/home/')
    poll.delete()
    messages.success(request, "Poll Deleted successfully",
                     extra_tags='alert alert-success alert-dismissible fade show')
    return redirect("/list/")


@login_required
def add_choice(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('/home/')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice added successfully", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('edit', poll.id)
    else:
        form = ChoiceAddForm()
    context = {
        'form': form,
    }
    return render(request, 'add_choice.html', context)


@login_required
def choice_edit(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('/home/')

    if request.method == 'POST':
        form = ChoiceAddForm(request.POST, instance=choice)
        if form.is_valid:
            new_choice = form.save(commit=False)
            new_choice.poll = poll
            new_choice.save()
            messages.success(
                request, "Choice Updated successfully", extra_tags='alert alert-success alert-dismissible fade show')
            return redirect('edit', poll.id)
    else:
        form = ChoiceAddForm(instance=choice)
    context = {
        'form': form,
        'edit_choice': True,
        'choice': choice,
    }
    return render(request, 'add_choice.html', context)


@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, pk=choice_id)
    poll = get_object_or_404(Poll, pk=choice.poll.id)
    if request.user != poll.owner:
        return redirect('/home/')
    choice.delete()
    messages.success(
        request, "Choice Deleted successfully", extra_tags='alert alert-success alert-dismissible fade show')
    return redirect('edit', poll.id)


def poll_detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if not poll.active:
        return render(request, 'poll_result.html', {'poll': poll})
    loop_count = poll.choice_set.count()
    context = {
        'poll': poll,
        'loop_time': range(0, loop_count),
    }
    return render(request, 'poll_detail.html', context)


@login_required
def poll_vote(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    choice_id = request.POST.get('choice')
    if not poll.user_can_vote(request.user):
        messages.error(
            request, "You already voted this poll", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("/list/")

    if choice_id:
        choice = Choice.objects.get(id=choice_id)
        vote = Vote(user=request.user, poll=poll, choice=choice)
        vote.save()
        print(vote)
        return render(request, 'poll_result.html', {'poll': poll})
    else:
        messages.error(
            request, "No choice selected", extra_tags='alert alert-warning alert-dismissible fade show')
        return redirect("polls:detail", poll_id)
    return render(request, 'poll_result.html', {'poll': poll})


@login_required
def endpoll(request, poll_id):
    poll = get_object_or_404(Poll, pk=poll_id)
    if request.user != poll.owner:
        return redirect('/home/')

    if poll.active is True:
        poll.active = False
        poll.save()
        return render(request, 'poll_result.html', {'poll': poll})
    else:
        return render(request, 'poll_result.html', {'poll': poll})

# Create your views here.
