from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from geniusback.models import *
from .serializers import createSerializer
from .utils import generate, generate_image
import logging

MembersSerializer = createSerializer(Members)
BooksSerializer = createSerializer(Books)
MyLibrarySerializer = createSerializer(MyLibrary)
DraftSerializer = createSerializer(Draft)
IntroSerializer = createSerializer(Intro)
DraftPageSerializer = createSerializer(DraftPage)
FeedBackSerializer = createSerializer(FeedBack)
FollowersSerializer = createSerializer(Followers)
FlowerSerializer = createSerializer(Flower)
MyForestSerializer = createSerializer(MyForest)
MyFlowerSerializer = createSerializer(MyFlower)


# temporary auth for API test
class LoginViewforAuth(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'logged in successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'invalid info'}, status=status.HTTP_401_UNAUTHORIZED)


class MembersViewSet(viewsets.ModelViewSet):
    queryset = Members.objects.all()
    serializer_class = MembersSerializer

    @action(detail=False, methods=['get'])
    def user_nickname(self, request):
        # calling user nickname
        user = request.user
        return Response({"user_nickname": user.nickname})

    @action(detail=False, methods=['get'])
    def user_id(self, request):
        # calling user id(PK)
        user = request.user
        return Response({"user_id": user.id})


# buying seeds
class PurchaseSeeds(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        seeds_for_purchase = request.data.get('seeds_for_purchase', 0)

        try:
            seeds_for_purchase = int(seeds_for_purchase)
        except ValueError:
            return Response({'error': '올바르지 않은 씨앗 값입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if seeds_for_purchase < 0:
            return Response({'error': '씨앗의 값이 0보다 작습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        user.seedCnt += int(seeds_for_purchase)
        user.save()
        return Response({'message': '씨앗 구매 성공!', '씨앗 개수': user.seedCnt})


# counting amount of seeds
class GetSeedsCount(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({'씨앗 개수': user.seedCnt})


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = BooksSerializer


class MyLibraryViewSet(viewsets.ModelViewSet):
    queryset = MyLibrary.objects.all()
    serializer_class = MyLibrarySerializer


class DraftViewSet(viewsets.ModelViewSet):
    queryset = Draft.objects.all()
    serializer_class = DraftSerializer

    @action(methods=['post'], detail=True)
    def choose_diff(self, request):
        draft = self.get_object()

        diff_count = request.data.get('diff_Count')
        if diff_count is None:
            return Response({'error': 'diff_Count is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            diff_count = int(diff_count)
            if not 3 <= diff_count <= 5:
                raise ValueError
        except ValueError:
            return Response({'error': 'invalid diff_Count. '
                                      'must be an integer between 3 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        draft.diff = diff_count
        draft.save()

        return Response({'message': "diff_Count updated successfully", 'diff': diff_count})


#GENRES = [
#    "fantasy", "science fiction", "mystery", "romance",
#    "horror", "thriller", "historical", "adventure"
#]


class IntroViewSet(viewsets.ModelViewSet):
    queryset = Intro.objects.all()
    serializer_class = IntroSerializer

    @action(detail=False, methods=['post'])
    def generate_subject(self,request):
        genre = request.data.get('genre')
        if not genre:
            return Response({'error': 'Genre is required'}, status=status.HTTP_400_BAD_REQUEST)
        subject_prompt = f"장르 {genre}에 기반한 세가지의 독특한 이야기 주제를 생성해."
        try:
            responses = generate(subject_prompt)
            if isinstance(responses, str):
                images = []
                subjects = responses.split('\n')
                for response in subjects:
                    if response.strip():
                        image_url = generate_image(response)
                        images.append(image_url)
                return Response({'topics': subjects, 'images': images})
            else:
                return Response({'error': 'Invalid response format'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def create_intro_content(self, request):
        draft_id = request.data.get('draft_id')
        user_id = request.data.get('user_id')
        intro_mode = request.data.get('introMode')
        selected_subject = request.data.get('selected_subject')
        if not draft_id:
            return Response({'error': 'Draft ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        draft = get_object_or_404(Draft, pk=draft_id)

        name_prompt = f"주제 {selected_subject}를 기반해서 주인공의 이름 세가지를 생성해."
        try:
            response = generate(name_prompt)
            if isinstance(response, str):
                protagonist_names = response.split('\n')
            else:
                return Response({'error': 'Invalid response format'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        intro = Intro(draft=draft, user_id=user_id, introMode=intro_mode,
                      subject=selected_subject, IntroContent=protagonist_names)
        intro.save()
        return Response({'intro_id': intro.id, 'subject': selected_subject,
                         'intro_content': protagonist_names})

    @action(detail=False, methods=['post'])
    def recreate_intro_content(self, request):
        draft_id = request.data.get('draft_id')
        user_id = request.data.get('user_id')
        intro_mode = request.data.get('introMode')
        selected_subject = request.data.get('selected_subject')
        if not draft_id:
            return Response({'error': 'Draft ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        draft = get_object_or_404(Draft, pk=draft_id)
        data=Intro.objects.all()
        data.delete()

        name_prompt = f"주제 {selected_subject}를 기반해서 주인공의 이름 세가지를 생성해."
        try:
            response = generate(name_prompt)
            if isinstance(response, str):
                protagonist_names = response.split('\n')
            else:
                return Response({'error': 'Invali   d response format'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        intro = Intro(draft=draft, user_id=user_id, introMode=intro_mode,
                      subject=selected_subject, IntroContent=protagonist_names)
        intro.save()
        return Response({'intro_id': intro.id, 'subject': selected_subject,
                         'intro_content': protagonist_names})

class DraftPageViewSet(viewsets.ModelViewSet):
    queryset = DraftPage.objects.all()
    serializer_class = DraftPageSerializer

    @action(detail=False, methods=['post'])
    def make_draft_page(self, request):
        draft_id = request.data.get('draft_id')
        user_id = request.data.get('user_id')
        diff=int(request.data.get('diff'))
        draft = get_object_or_404(Draft, pk=draft_id)
        selected_subject = request.data.get('selected_subject')
        intro_content = request.data.get('intro_content')
        if not draft_id:
            return Response({'error': 'Draft ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        latest_page = DraftPage.objects.filter(draft=draft).order_by('-pageNum').first()
        if latest_page:
            total_pages = latest_page.pageNum + 1
        else:
            total_pages = 1

        if total_pages < 9:
            if total_pages == 1:
                alpha_question_prompt = (
                    f"주인공의 이름은 {intro_content}이다. "
                    f"{intro_content}에게 어떤 일이 일어날지에 대한 질문을 한가지만 해.")
                try:
                    response = generate(alpha_question_prompt)
                    if isinstance(response, str):
                        alpha_question = response.split('\n')
                    else:
                        return Response({'error': 'Invalid response format'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                beta_question_prompt = (f"지금까지의 줄거리 {selected_subject}와 "
                                        f"이야기 관련 질문 {alpha_question}을 보고, "
                                        f"그 질문에 부합하면서 창의적인 답변을 {diff}개만 생성해.")
                try:
                    response = generate(beta_question_prompt)
                    if isinstance(response, str):
                        beta_answer = response.split('\n')
                    else:
                        return Response({'error': 'Invalid response format'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                new_page = DraftPage.objects.create(draft=draft, user_id=user_id, pageNum=total_pages,
                                                    pageContent=alpha_question)

                return Response({
                    'first_question': alpha_question,
                    'answers': beta_answer,
                    'page_num': total_pages,
                    'page_id': new_page.id
                })


            else:
                context = ' '.join(
                    [page.pageContent for page in DraftPage.objects.filter(draft=draft).order_by('pageNum')])
                first_question_prompt = (f"지금까지의 줄거리야 : {context}. 이를 기반으로, "
                                         f"이야기를 전개시키기 위해 이야기와 관련된 질문을 한가지만 해.")

                try:
                    response = generate(first_question_prompt)
                    if isinstance(response, str):
                        first_question = response.split('\n')
                    else:
                        return Response({'error': 'Invalid response format'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                second_question_prompt = (f"지금까지의 줄거리 {context}와 이야기 관련 질문 {first_question}을 보고, "
                                          f"그 질문에 부합하면서 창의적인 답변을 {diff}개만 생성해.")
                try:
                    response = generate(second_question_prompt)
                    if isinstance(response, str):
                        semi_final_answer = response.split('\n')
                    else:
                        return Response({'error': 'Invalid response format'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                new_page = DraftPage.objects.create(draft=draft, user_id=user_id,
                                                    pageNum=total_pages, pageContent=first_question)

                return Response({
                    'next_question': first_question,
                    'answers': semi_final_answer,
                    'page_num': total_pages,
                    'page_id': new_page.id
                })

        else:
            return Response({'message': "the story is ended"})

    @action(detail=False, methods=['post'])
    def finish_draft_page(self, request):
        draft_id = request.data.get('draft_id')
        user_id = request.data.get('user_id')
        diff = int(request.data.get('diff'))
        draft = get_object_or_404(Draft, pk=draft_id)
        latest_page = DraftPage.objects.filter(draft=draft).order_by('-pageNum').first()
        total_pages = latest_page.pageNum + 1
        if not draft_id:
            return Response({'error': 'Draft ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        context = ' '.join(
            [page.pageContent for page in DraftPage.objects.filter(draft=draft).order_by('pageNum')])
        final_question_prompt = (f"지금까지의 줄거리야 : {context}. 이를 기반으로, "
                                 f"이야기를 마무리하기 위한 질문을 한가지만 해.")
        try:
            response = generate(final_question_prompt)
            if isinstance(response, str):
                final_question = response.split('\n')
            else:
                return Response({'error': 'Invalid response format'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        final_answer_prompt = (f"지금까지의 줄거리 {context}와 동화의 마지막 이야기를 장식할 질문 {final_question}을 보고, "
                                  f"그 질문에 부합하면서 창의적인 답변을 {diff}개만 생성해.")
        try:
            response = generate(final_answer_prompt)
            if isinstance(response, str):
                final_answer = response.split('\n')
            else:
                return Response({'error': 'Invalid response format'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        new_page = DraftPage.objects.create(draft=draft, user_id=user_id,
                                            pageNum=total_pages, pageContent=final_question)

        return Response({
            'final_question': final_question,
            'answers': final_answer,
            'page_id': new_page.id
        })
class FeedBackViewSet(viewsets.ModelViewSet):
    queryset = FeedBack.objects.all()
    serializer_class = FeedBackSerializer


class FollowersViewSet(viewsets.ModelViewSet):
    queryset = Followers.objects.all()
    serializer_class = FollowersSerializer


class FlowerViewSet(viewsets.ModelViewSet):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer


class MyForestViewSet(viewsets.ModelViewSet):
    queryset = MyForest.objects.all()
    serializer_class = MyForestSerializer


class MyFlowerViewSet(viewsets.ModelViewSet):
    queryset = MyFlower.objects.all()
    serializer_class = MyFlowerSerializer
# Create your views here.
