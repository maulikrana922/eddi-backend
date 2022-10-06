from eddi_backend.settings import BASE_DIR
import environ
env = environ.Env()
environ.Env.read_env()
ENV = env('DJANGO_ENV')
if ENV == 'development':
    FRONT_URL = 'https://eddi-frontend.testyourapp.online/'
    SUPPLIER_URL = 'https://eddi-supplier.testyourapp.online/#/'
    STRIPE_PROFILE_LINK = f'https://connect.stripe.com/express/oauth/authorize?response_type=code&client_id=ca_MBSpisruDRjLebOHkMle2ampUcXauh9n&scope=read_write&state={{uuid}}#/'
else:
    FRONT_URL = 'https://eddistaging-frontend.testyourapp.online/'
    SUPPLIER_URL = 'https://eddistaging-supplier.testyourapp.online/#/'

FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
EMAIL_ID = 'email_id'
CARD_TYPE = 'card_type'
AMOUNT = 'amount'
PRICE = 'price'
PAYMENT_METHOD_ID = 'payment_method_id'
STATUS_ID = 'status_id'
IS_DELETED = "is_deleted"
IS_LOGIN_FROM ="is_login_from"
UUID = 'uuid'
PASSWORD = 'password'
DEVICE_TOKEN = 'device_token'
STATUS = 'status'
DATA = 'data'
DATA_SV = 'data_sv'
SUCCESS = 'success'
ERROR = 'error'
IS_FIRST_TIME_LOGIN ='is_first_time_login'
IS_STUDENT = 'is_student'
IS_SUPPLIER = 'is_supplier'
IS_ADMIN = 'is_admin'
IS_SWEDISHDEFAULT = 'is_swedishdefault' 
MODIFIED_AT = 'modified_date_time'
MODIFIED_BY = 'modified_by'
CREATED_AT='created_date_time'
CREATED_BY='created_by'
POST_METHOD = 'POST'
COURSE_IMAGE = 'course_image'
COURSE_NAME = 'course_name'
COURSE_LEVEL_ID = 'course_level_id'
COURSE_LENGTH = 'course_length'
COURSE_CATEGORY_ID = 'course_category_id'
COURSE_CATEGORY_NAME = 'course_category_category_name'
COURSE_TYPE_ID = 'course_type_id'
AUTHOR_NAME = 'author_name'
AUTHOR_BIO = 'author_bio'
FEE_TYPE_NAME = 'fee_type_name'
FEE_TYPE_ID = 'fee_type_id'
COURSE_PRICE='course_price'
LEVEL_NAME = 'level_name'
ADDITIONAL_INFORMATION='additional_information'
TYPE_NAME = 'type_name'
ID = 'id'
SUBCATEGORY_NAME_ID='subcategory_name_id'
CATEGORY_NAME_ID = 'category_name_id'
COURSE_SUBCATEGORY_ID = 'course_subcategory_id'
SUBCATEGORY_NAME='subcategory_name'
SUBCATEGORY_IMAGE = 'subcategory_image'
CATEGORY_NAME = 'category_name'
TRUE = 'true'
FALSE = 'false'
OTP_EMAIL_HTML = 'otp-password.html'
COURSE_ENROLL_HTML_TO_S = "course_enroll_to_supplier.html"
CONTACT_LEAD = "contact_lead.html"
APPROVE_COURSE_HTML = "approve_course.html"
INACTIVE_COURSE = "inactive_course.html"
EVENT_ENROLL_HTML = "event_enroll.html"
COURSE_ENROLL_HTML_TO_U = "course_enroll_to_user.html"
SESSION_INVITATION = "session_invitation.html"
INVOICE_HTML = "invoice.html"
INVOICE_TO_USER = 'invoice-to-user.html'
VERIFY_EMAIL = 'verify_email.html'
USER_ACTIVATED = 'user-activated.html'
USER_DEACTIVATED = 'user-deactivated.html'
USER_WELCOME ='user-welcome.html'
RESETPASSWORD_HTML = 'resetpassword-link.html'
RESETPASSWORDSupplierAdmin_HTML = 'reset-password-supplierAdmin.html'
SUPPLIER_WITHDRAW_REQUEST_HTML = 'supplier_withdraw_request.html'
SUPPLIER_WITHDRAW_REQUEST_ADMIN = 'supplier_withdraw_request_admin.html'
SUPPLIER_WITHDRAW_REQUEST_HOLDBY_ADMIN = 'supplier_withdraw_request_holdby_admin.html'
SUPPLIER_PAYOUT_SUCCESSED_HTML = 'supplier_payout_succeeded.html'
CONTACTUS_USER = 'contactus_user.html'
USER_TYPE_ID = 'user_type_id'
ORGANIZATION_LOCATION = 'organization_location'
SUB_AREA = 'sub_area'
SUPPLIER_ID = 'supplier_id'
SUPPLIER_S = 'Supplier'
ADMIN_S = 'Admin'
FULLNAME = 'fullname'
USER_TYPE='user_type'
BLOG_CATEGORY_ID='blog_category_id'
PHONE_NUMBER = 'phone_number'
USER_LOCATION = "user_location"
USER_INTERESTS = "user_interests"
LOCATION = "location"
COURSE_CHECKOUT_LINK = 'course_checkout_link'
COURSE_FOR_ORGANIZATION='course_for_organization'
COURSE_LANGUAGE='course_language'
ORIGINAL_PRICE='original_price'
MESSAGE = 'message'
ORGANIZATION_DOMAIN = 'organization_domain'
EVENT_IMAGE = "event_image"
EVENT_PUBLISH_ON = "event_publish_on"
EVENT_NAME = "event_name"
EVENT_CHOOSE_TYPE = "event_choose_type"
EVENT_CATEGORY = "event_category"
BANNER_VIDEO_LINK = "banner_video_link"
START_DATE = "start_date"
END_DATE = "end_date"
START_TIME = "start_time"
END_TIME = "end_time"
FEES_TYPE = "fees_type"
EVENT_TYPE = "event_type"
EVENT_PRICE = "event_price"
CHECKOUT_LINK = "checkout_link"
MEETING_LINK = "meeting_link"
MEETING_PASSCODE = "meeting_passcode"
IS_POST = "is_post"
VAR_CHARGES = "var_charges"
EVENT_SMALL_DESCRIPTION = "event_small_description"
EVENT_DESCRIPTION = "event_description"
EVENT_LOCATION = "event_location"
EVENT_ORGANIZER = "event_organizer" 
EVENT_SUBSCRIBER = "event_subscriber"
IS_FEATURED = "is_featured"
VIDEO_TITLE = 'video_title'
VIDEO_FILES = 'video_files'
VIDEO_FILES_ID = 'video_files_id'
FILE_TITLE = 'file_title'
DOCUMENT_FILES  = 'document_files'
DOCUMENT_FILES_ID = 'document_files_id'
PAYMENT_INTENT = 'payment_intent'
EXTRA_MSG = 'extra_msg'
CARD_BRAND = 'card_brand'
USER_PROFILE = 'user_profile'
EVENT_DATA = 'event_data'
COURSE_CATEGORY = 'course_category'
SUPPLIER_EMAIL = 'supplier_email'
PAYMENT_DETAIL_ID = 'payment_detail_id'
USER_PROFILE_ID = 'user_profile_id'
USERPROFILE = 'UserProfile'
RELATED_BLOG = 'related_blog'
ADMIN_EMAIL = 'admin_email'
IS_FAVOURITE = 'is_favourite'
SUPPLIER_EMAIL_ID = 'supplier_email_id'
SUBSCRIBER_COUNT = 'subscriber_count'

RECRUITMENTAD_FILE = 'recruitmentAd_File'
RECRUITMENTAD_TITLE = 'recruitmentAd_title'
RECRUITMENTAD_DESCRIPTION = 'recruitmentAd_description'
RECRUITMENTAD_BANNER_VIEDO_LINK = 'recruitmentAd_banner_video_link'
RECRUITMENTAD_EXPIRY = 'recruitmentAd_Expiry'
SUPPLIER_PROFILE = "supplier_profile"
IS_APPROVED_ID = 'is_approved_id'
COURSE_STARTING_DATE = 'course_starting_date'
APPROVAL_STATUS = 'approval_status'
IS_APPROVED = 'is_approved'
TARGET_USERS="target_users"
USERNAME = 'username'
COURSENAME = 'coursename'
USER_EMAIL = 'user_email'
COURSE_ID = 'course_id'
COURSETYPE = 'coursetype'
TIME_PERIOD = 'time_period'
WEEKLY = 'weekly'
YEARLY = 'yearly'
MONTHLY = 'monthly'
TOTAL_COURSE_COUNT = 'total_course_count'
TOTAL_USER_COUNT = 'total_user_count'
SUPPLIER_COURSE_COUNT = 'supplier_course_count'
PURCHASED_COURSE_COUNT = 'purchased_course_count'
COURSE_OFFERED = 'Course_Offered'
INDIVIDUALS = 'Individuals'
ALL_SUBCATEGORY = 'all_subcategory'
PURCHASED = 'Purchased'
NOT_PURCHASED = 'Not_Purchased'
ENROLLED = 'Enrolled'
COURSE = 'course'

PROFILE_IMAGE = 'profile_image'
GENDER = 'gender'
DOB = 'dob'
PERSONAL_NUMBER = 'personal_number'
HIGHEST_EDUCATION = 'highest_education'
UNIVERSITY_NAME = 'university_name'
HIGHEST_DEGREE = 'highest_degree'
EDUCATIONAL_AREA = 'educational_area'
OTHER_EDUCATION = 'other_education'
DIPLOMAS_CERTIFICATES = 'diplomas_certificates'
CURRENT_PROFESSIONAL_ROLE = 'current_professional_role'
ADDITIONAL_ROLE = 'additional_role'
EXTRA_CURRICULAR = 'extra_curricular'
EXTRA_CURRICULAR_COMPETENCE = 'extra_curricular_competence'
CORE_RESPONSIBILITIES = 'core_responsibilities'
LEVEL_OF_ROLE = 'level_of_role'
FUTURE_PROFESSIONAL_ROLE = 'future_professional_role'
AREA_OF_INTEREST = 'area_of_interest'
AGREE_ADS_TERMS = 'agree_ads_terms'

ORGANIZATIONAL_NAME = 'organizational_name'
ORGANIZATION_EMAIL = 'organization_email'
ORGANIZATION_WEBSITE = 'organization_website'
ORGANIZATION_ADDRESS = 'organization_address'
COUNTRY = 'country'
CITY = 'city'
BRIF_INFORMATION = 'brif_information'
ORGANIZATION_PHONE_NUMBER = 'organization_phone_number'
CONTECT_PERSON = 'contact_person'
SUB_CATEGORY = 'sub_category'
ORGANIZATION_LOGO = 'organization_logo'

SUPPLIER_NAME = 'supplier_name'
ADDRESS = 'address'
SUPPLIER_IMAGE = 'supplier_image'
ABOUT_ME = "about_me"
USER_UUID = 'user_uuid'
BATCH_NAME = 'batch_name'
BATCH_SESSION = 'BatchSession'
SESSION_NAME = 'session_name'
COURSE_BATCH = 'CourseBatch'
BATCH = 'batch'
TOTAL_DURATION = 'total_duration'
URL = 'url'
CHOOSE_DAYS = 'choose_days'
EVENT_ID = 'event_id'
CUSTOM_DAYS = 'customDays'


SCOPES = ['https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = str(BASE_DIR) +'/creds2.json'
