from doctest import FAIL_FAST
import email
from email.mime.image import MIMEImage
from django.urls import is_valid_path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import json
from eddi_app.permissions import IsValid
from .serializers import *
from eddi_app import models
from eddi_app.constants.constants import *
from eddi_app.constants.table_name import *
import datetime
from django.db.models import Q
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password, check_password
from .supplier_views import *
from uuid import uuid4
import stripe # 2.68.0
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

stripe.api_key = settings.STRIPE_SECRET_KEY


@permission_classes([AllowAny])
class Save_stripe_info(APIView):
    def post(self, request, *args, **kwargs):
            if request.method == "POST":
                # data = request.data
                email_id = request.POST.get("email_id")
                card_type = request.POST.get("card_brand")
                amount = request.POST.get("price")
                payment_method_id = request.POST.get("payment_method_id")
                course_name = request.POST.get("course_name")
                
                extra_msg = ''
                # checking if customer with provided email already exists
                try:
                    var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_name,STATUS:'Success'})
                    print(var, "varrrrrrr")
                    if var is not None:
                        return Response({MESSAGE: "ERROR", DATA: "You already Enrolled"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as ex:
                    print(ex, "exxxxxxxxxxxxxxxxx")
                    pass
                
                try:
                    print("inside first try")
                    customer_data = stripe.Customer.list(email=email_id).data
                    if len(customer_data) == 0:
                        # creating customer
                        customer = stripe.Customer.create(email=email_id, payment_method=payment_method_id)
                    else:
                        customer = customer_data[0]
                        extra_msg = "Customer already existed."
                        
                    # creating paymentIntent
                    try:
                        print("inside second try")

                        intent = stripe.PaymentIntent.create(
                        amount=int(1)*100,
                        currency='usd',
                        description='helllo',
                        customer=customer['id'],
                        payment_method_types=["card"],
                        payment_method=payment_method_id,
                        confirm=True)
                        print(intent, "intenttttt")
                        print("inside second try last")

                    except Exception as e:
                        print(e)
                        return Response({MESSAGE: "ERROR", DATA: "ERROR"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                    
                    print("okkkkk")
                    return Response({MESSAGE: SUCCESS, DATA: {'payment_intent':intent, 'extra_msg': extra_msg}}, status=status.HTTP_200_OK,)
                except Exception as e:
                    # print(e)
                    return Response({MESSAGE: ERROR, DATA: "ERROR"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({MESSAGE: 'Invalid Request', DATA: "error"}, status=status.HTTP_400_BAD_REQUEST)

   
class UserSignupView(APIView):
    def post(self, request):
        record_map = {}
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_type_id = getattr(models,USER_TYPE_TABLE).objects.only(ID).get(**{USER_TYPE:request.POST.get(USER_TYPE,None)})
        except:
            return Response({STATUS:ERROR, DATA: "Error Getting User Type"}, status=status.HTTP_400_BAD_REQUEST)
        
        record_map = {
            FIRST_NAME: request.POST.get(FIRST_NAME,None),
            LAST_NAME: request.POST.get(LAST_NAME,None),
            EMAIL_ID: request.POST.get(EMAIL_ID,None),
            PASSWORD: make_password(request.POST.get(PASSWORD)),
            
            USER_TYPE_ID: user_type_id.id,
            STATUS_ID:1
        }
        record_map[CREATED_AT] = make_aware(datetime.datetime.now())
        record_map[CREATED_BY] = 'admin'
        try:
            getattr(models,USERSIGNUP_TABLE).objects.update_or_create(**record_map)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "User Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)


class GetUserDetails(APIView):
    def post(self, request):
        record_map = {}
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.filter(**{'user_type__user_type':request.POST.get('user_type')})
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "No data found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)


    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
            if serializer := UserSignupSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            data = getattr(models,USERSIGNUP_TABLE).objects.all()
            if serializer := UserSignupSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,uuid = None):  # sourcery skip: class-extract-method
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            EMAIL_ID: request.FILES.get(EMAIL_ID,data.email_id),
            PASSWORD: request.POST.get(PASSWORD,data.password),
            USER_TYPE_ID: 2,
            IS_FIRST_TIME_LOGIN : request.POST.get(IS_FIRST_TIME_LOGIN,data.is_first_time_login),
            STATUS_ID:request.POST.get(STATUS_ID,data.status)
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Edited"}, status=status.HTTP_200_OK)

    def delete(self,request,uuid = None):
        if not uuid:
            return Response({STATUS: ERROR, DATA: "Not Able to get data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid,STATUS:1})
        except:
            return Response({STATUS: ERROR, DATA: "Data Not Found"}, status=status.HTTP_400_BAD_REQUEST)
        record_map = {
            EMAIL_ID: request.FILES.get(EMAIL_ID,data.email_id),
            PASSWORD: request.POST.get(PASSWORD,data.password),
            USER_TYPE_ID: 2,
            IS_FIRST_TIME_LOGIN : request.POST.get(IS_FIRST_TIME_LOGIN,data.is_first_time_login),
            STATUS_ID:2
        }
        record_map[MODIFIED_AT] = make_aware(datetime.datetime.now())
        record_map[MODIFIED_BY] = 'admin'
        record_map[UUID] = uuid4()
        for key,value in record_map.items():
            setattr(data,key,value)
        data.save()
        return Response({STATUS: SUCCESS, DATA: "Data Succesfully Deleted"}, status=status.HTTP_200_OK)
   
@permission_classes([AllowAny])
class UserLoginView(APIView):
    def post(self, request):
        # sourcery skip: assign-if-exp, reintroduce-else, swap-if-expression
        email_id = request.POST.get(EMAIL_ID)
        password = request.POST.get(PASSWORD)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1})
            token = NonBuiltInUserToken.objects.create(user_id = data.id)
            print(token.key)

            

            print(data.user_type)
        except Exception as ex:
            print(ex)
            data = None
        try:
            user_profile = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            if user_profile:
                user_profile = True
        except Exception as ex:
            print(ex)
            user_profile = False
        serializer = UserSignupSerializer(data)
        if serializer and data:
            if not check_password(password, data.password):
                return Response({STATUS: ERROR, DATA: "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
 
            return Response({STATUS: SUCCESS, DATA: True, DATA: {"FIRST_NAME":data.first_name, "LAST_NAME":data.last_name} ,"user_type":str(data.user_type),IS_FIRST_TIME_LOGIN: data.is_first_time_login,"user_profile":user_profile,"Authorization":"Token "+ str(token.key)}, status=status.HTTP_200_OK)
           
        else:
            return Response({STATUS: ERROR, DATA: "User Not Found"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class ForgetPasswordView(APIView):
    def post(self, request,uuid = None):
        email_id = request.POST.get(EMAIL_ID)
        request.session['forget-password'] = email_id
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1})
        except:
            data = None
        try:
            if data:
                if request.session.has_key('forget-password'):
                    html_path = RESETPASSWORD_HTML
                    context_data = {"final_email": email_id}
                    email_html_template = get_template(html_path).render(context_data)
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = (email_id,)
                    email_msg = EmailMessage('Welcome to Eddi',email_html_template,email_from,recipient_list)
                    email_msg.content_subtype = 'html'

                    path = 'eddi_app'
                    img_dir = 'static'
                    image = 'Logo.jpg'
                    file_path = os.path.join(path,img_dir,image)
                    with open(file_path,'rb') as f:
                        img = MIMEImage(f.read())
                        img.add_header('Content-ID', '<{name}>'.format(name=image))
                        img.add_header('Content-Disposition', 'inline', filename=image)
                    email_msg.attach(img)
                    print("ok")
                    email_msg.send(fail_silently=False)
                    return Response({STATUS: SUCCESS, DATA: "Email Sent Successfully"}, status=status.HTTP_200_OK) 
            else:
                return Response({STATUS: ERROR, DATA: "You are not a registered user"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex)
            return Response({STATUS: ERROR, DATA: 'error'}, status=status.HTTP_400_BAD_REQUEST)
                
        
class ResetPasswordView(APIView):
    def post(self,request,slug=None):
        email_id = request.POST.get(EMAIL_ID)
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{EMAIL_ID:email_id,STATUS_ID:1})
            password = request.POST.get(PASSWORD)
        except:
            data = None
        try:
            if data:
                setattr(data,PASSWORD,make_password(password))
                setattr(data,IS_FIRST_TIME_LOGIN,False)

                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password Changed Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ex}, status=status.HTTP_400_BAD_REQUEST)



class ChangePasswordView(APIView):
    def post(self,request,uuid):
        try:
            data = getattr(models,USERSIGNUP_TABLE).objects.get(**{UUID:uuid})
            password = request.POST.get(PASSWORD)
        except:
            data = None
        try:
            if data:
                setattr(data,PASSWORD,make_password(password))
                setattr(data,IS_FIRST_TIME_LOGIN,False)

                setattr(data,MODIFIED_AT,make_aware(datetime.datetime.now()))
                setattr(data,MODIFIED_BY,'admin')
                data.save()
                return Response({STATUS: SUCCESS, DATA: "Password Changed Successfull"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Invalid Request"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({STATUS: ERROR, DATA: ex}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsValid])
class GetHomePageDetails(APIView):

    def get(self, request):
        data = getattr(models,HOMEPAGECMS_TABLE).objects.latest('created_date_time')
        if not (serializer := HomePageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)


class GetPrivacyPolicyDetails(APIView): 
    def get(self, request):
        data = getattr(models,PRIVACY_POLICY_CMS_TABLE).objects.latest('created_date_time')
        if not (serializer := PrivacyPolicyPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        print(serializer, "serializeerrrrrrrrrr")
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)

class GetTermsConditionDetails(APIView): 
    def get(self, request):
        data = getattr(models,TERMS_CONDITION_CMS_TABLE).objects.latest('created_date_time')
        if not (serializer := TermsConditionPageCMSSerializer(data)):
            return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        print(serializer, "serializeerrrrrrrrrr")
        return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
       
class GetAboutUsPageDetails(APIView):
    def get(self, request):
            data = getattr(models,ABOUTUSCMS_TABLE).objects.latest('created_date_time')
            if serializer := AboutUsCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class GetContactUsPageDetails(APIView):
    def get(self, request):
            data = getattr(models,CONTACTUSCMS_TABLE).objects.latest('created_date_time')
            if serializer := ContactUsCMSSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
 
class GetBlogDetails(APIView):
    def get(self, request,uuid = None):
        if uuid:
            data = getattr(models,BLOGDETAILS_TABLE).objects.get(**{UUID:uuid})
            try:
                related_blog = list(getattr(models,BLOGDETAILS_TABLE).objects.filter(**{BLOG_CATEGORY_ID:data.blog_category.id}).order_by('-created_date_time').exclude(id = data.id).values())
                for i in related_blog:
                    for key,value in i.items():
                        if key == 'blog_image':
                            i[key] = "/media/" + value
            except:
                related_blog = []
            
            if serializer := BlogDetailsSerializer(data):
                
                return Response({STATUS: SUCCESS, DATA: serializer.data, 'related_blog':related_blog}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            
            data = getattr(models,BLOGDETAILS_TABLE).objects.all()
            if serializer := BlogDetailsSerializer(data, many=True):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ContactFormView(APIView):
    def post(self, request):
        if request.method != POST_METHOD:
            return Response({STATUS: ERROR, DATA: "Error"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            record_map = {
                FULLNAME : request.POST.get(FULLNAME),
                EMAIL_ID : request.POST.get(EMAIL_ID),
                PHONE_NUMBER : request.POST.get(PHONE_NUMBER),
                MESSAGE : request.POST.get(MESSAGE)
            }

            record_map[CREATED_AT] = make_aware(datetime.datetime.now())
            record_map[CREATED_BY] = 'admin'
            try:
                getattr(models,CONTACT_FORM_TABLE).objects.update_or_create(**record_map)
            except Exception as ex:
                print(ex)
                return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({STATUS: ERROR, DATA: "Error in getting data"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    def post(self, request):

        # sourcery skip: remove-unnecessary-else, swap-if-else-branches
        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({STATUS: ERROR, DATA: "Error While Saving Data"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.POST:
            email_id = request.POST.get(EMAIL_ID)
            data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            if serializer := UserProfileSerializer(data):
                return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if request.POST:
            email_id = request.POST.get(EMAIL_ID)
            instance = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
            serializer = UserProfileSerializer(instance,data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Error While editing data"}, status=status.HTTP_400_BAD_REQUEST)
            
            
@permission_classes([AllowAny])
class UserPaymentDetail_info(APIView):
    def post(self, request):
        try:
            email_id = request.POST.get("email_id")
            card_type = request.POST.get("card_brand")
            amount = request.POST.get("price")
            status_s = request.POST.get("status")
            course_name = request.POST.get("course_name")
           
                
            record_map = {}
            record_map = {
                COURSE_NAME : course_name,
                EMAIL_ID: email_id,
                CARD_TYPE : card_type,
                AMOUNT: float(amount),
                STATUS: status_s,
                CREATED_AT : make_aware(datetime.datetime.now())
                }
            print(record_map, "recordddd")
            try:
                var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_name,STATUS:'Success'})
                print(var, "varrrrrr")
            except Exception as ex:
                print("Data not found")
                var = None
            if not var:
                try:
                    getattr(models,USER_PAYMENT_DETAIL).objects.update_or_create(**record_map)
                    profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:email_id})
                    var = getattr(models,USER_PAYMENT_DETAIL).objects.get(**{EMAIL_ID:email_id, COURSE_NAME:course_name,STATUS:'Success'})
                    print("profile dataaaaaa")
                    record_map = {}
                    record_map = {
                    "payment_detail_id": var.id,
                    "user_profile_id" : profile_data.id,
                    CREATED_AT : make_aware(datetime.datetime.now())
                    }
                    print(record_map, "mapppppppppppp")
                    getattr(models,COURSE_ENROLL_TABLE).objects.update_or_create(**record_map)
                    print("Enrolll createdddd")
                    print("created")
                    return Response({STATUS: SUCCESS, DATA: "Created successfully"}, status=status.HTTP_200_OK)

                except Exception as e:
                    print(e)
                    
                    return Response({MESSAGE: "Error", DATA: "Data Creation Error"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({MESSAGE: "Error", DATA: "You Already Enrolled"}, status=status.HTTP_400_BAD_REQUEST)
                
                

        except Exception as ex:
            print(ex, "eeeee")
            return Response({DATA: "ERROR"}, status=status.HTTP_400_BAD_REQUEST)
                
              
            
class FavCourseDetails(APIView):
    def post(self, request):
        data = None
        email_id = None
        user_data_fav = None
        is_favourite_data = None
        record_map = {}
        token_data = request.headers.get('Authorization')
        token = token_data.split()[1]

        
        try:
            data = getattr(models,TOKEN_TABLE).objects.get(key = token)
            email_id = data.user.email_id
            print(data.key)
        except Exception as ex:
            print(ex)
            email_id = None
            return Response({MESSAGE: "Error", DATA: "Token Error"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            course_name = request.POST.get('course_name')
            user_data_fav = getattr(models,FAVOURITE_COURSE_TABLE).objects.filter(**{'course_name':course_name}).get(**{EMAIL_ID:email_id})
            print(user_data_fav)
        except Exception as ex:
            print(ex)
            user_data_fav = None
            
        if user_data_fav:
            fav_data = request.POST.get("is_favourite")
            print(fav_data)
            
            if fav_data == 'true':
                setattr(user_data_fav,'is_favourite',True)
                user_data_fav.save()
            else:
                setattr(user_data_fav,'is_favourite',False)
                user_data_fav.save()
        else:
            course_name = request.POST.get("course_name")
            fav_data = request.POST.get("is_favourite")
            
            if fav_data == 'true':
                print("TRUE")
                is_favourite_data = True
            else:
                print("FALSE")
                is_favourite_data = False
                
            record_map = {
                EMAIL_ID: email_id,
                "course_name" : course_name,
                "is_favourite": is_favourite_data,
                CREATED_AT : make_aware(datetime.datetime.now())
                }
            try:
                getattr(models,FAVOURITE_COURSE_TABLE).objects.update_or_create(**record_map)
                print("TRUEEEEEE")
                return Response({MESSAGE: SUCCESS, DATA: "Created"}, status=status.HTTP_200_OK)
                
            except Exception as e:
                print(e)
                return Response({MESSAGE: "Error", DATA: "ERROR creating data"}, status=status.HTTP_400_BAD_REQUEST)
                
                
        return Response({MESSAGE: "SUCCESS", DATA: "Done"}, status=status.HTTP_200_OK)
            
            
class ViewIndividualProfile(APIView):
    def post(self, request):
        user_email_id = request.POST.get("email_id")
        supplier_email_id = request.POST.get("supplier_email_id")
        token_data = request.headers.get('Authorization')
        token = token_data.split()[1]
        
        try:
            data = getattr(models,TOKEN_TABLE).objects.get(key = token)
            email_id = data.user.email_id
            print(data.key)
        except Exception as ex:
            print(ex)
            email_id = None
            return Response({MESSAGE: "Error", DATA: "Token Error"}, status=status.HTTP_400_BAD_REQUEST)
        
        # try:
        #     profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})
        #     print("TRUEEEEEE")
        #     # return Response({MESSAGE: SUCCESS, DATA: "Created"}, status=status.HTTP_200_OK)
                
        # except Exception as ex:
        #     print(ex, "Exxxxxxxxxxxxxxx")
        #     return Response({MESSAGE: "Error", DATA: "ERROR getting profile data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            supplier_course = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id": supplier_email_id})
            # print(supplier_course, "courseeeeeee")
            # course_list = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__email_id":user_email_id, "payment_detail__course_name":supplier_course.course_name})
            # course_list = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__email_id":user_email_id})
            # course_list = models.CourseEnroll.objects.filter(payment_detail__course_name__in=models.CourseDetails.objects.all())
            course_list = models.CourseDetails.objects.filter(course_name__in=models.CourseEnroll.objects.all())
            print(course_list, "cooooooooo")
            
            # for i in supplier_course:
            #     if i.course_name in [j.payment_detail.course_name for j in course_list]:
            #         print("okkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
                # print(i.course_name, "iiiii")
        except Exception as ex:
            print(ex, "exxx")
        
        try:
            profile_data = getattr(models,USER_PROFILE_TABLE).objects.get(**{EMAIL_ID:user_email_id})
            try:
                # course_list = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"user_profile__email_id":user_email_id})
                # course_list = getattr(models,COURSE_ENROLL_TABLE).objects.filter(**{"payment_detail__email_id":user_email_id, "payment_detail__course_name":supplier_course.course_name})
                # print(course_list, "cooooooooo")
                # course_list = getattr(models,COURSEDETAILS_TABLE).objects.filter(**{"supplier__email_id":user_email_id})
                pass
            except Exception as ex:
                print(ex, "exxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                return Response({STATUS: ERROR, DATA: "course list Error"}, status=status.HTTP_400_BAD_REQUEST)
                
            # print(profile_data, "profilllllll")
            # data = getattr(models,BLOGDETAILS_TABLE).objects.all()
            # if serializer := BlogDetailsSerializer(data, many=True):
            #     return Response({STATUS: SUCCESS, DATA: serializer.data}, status=status.HTTP_200_OK)
            if serializer := UserProfileSerializer(profile_data):
                if serializer1 := CourseEnrollSerializer(course_list, many=True):
                # if serializer1 := CourseDetailsSerializer(course_list, many=True):
                    # print(serializer, "seeeeee")
                    return Response({STATUS: SUCCESS, DATA: serializer.data, "Course":serializer1.data}, status=status.HTTP_200_OK)
            else:
                return Response({STATUS: ERROR, DATA: "Serializing data Error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            print(ex, "exxxxx")
        return Response({MESSAGE: "SUCCESS", DATA: "Done"}, status=status.HTTP_200_OK)
