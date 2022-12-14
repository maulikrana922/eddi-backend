# Generated by Django 4.0.3 on 2022-06-01 05:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eddi_app', '0124_notification_message_sv'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aboutuspagecms',
            options={'verbose_name_plural': 'About Us Page'},
        ),
        migrations.AlterModelOptions(
            name='aboutuspagecms_sv',
            options={'verbose_name_plural': 'About Us Page SV'},
        ),
        migrations.AlterModelOptions(
            name='approval_status',
            options={'verbose_name_plural': 'Approval Status Table'},
        ),
        migrations.AlterModelOptions(
            name='blogdetails',
            options={'verbose_name_plural': 'Blog Table'},
        ),
        migrations.AlterModelOptions(
            name='blogdetails_sv',
            options={'verbose_name_plural': 'Blog Table SV'},
        ),
        migrations.AlterModelOptions(
            name='contactformlead',
            options={'verbose_name_plural': 'Contact Form Lead Table'},
        ),
        migrations.AlterModelOptions(
            name='contactformlead_sv',
            options={'verbose_name_plural': 'Contact Form Lead Table SV'},
        ),
        migrations.AlterModelOptions(
            name='contactuspagecms',
            options={'verbose_name_plural': 'Contact Us Page'},
        ),
        migrations.AlterModelOptions(
            name='contactuspagecms_sv',
            options={'verbose_name_plural': 'Contact Us Page SV'},
        ),
        migrations.AlterModelOptions(
            name='coursecategorydetails',
            options={'verbose_name_plural': 'Course Category Table'},
        ),
        migrations.AlterModelOptions(
            name='coursedetails',
            options={'verbose_name_plural': 'Course Details Table'},
        ),
        migrations.AlterModelOptions(
            name='courseenroll',
            options={'verbose_name_plural': 'Course Enroll'},
        ),
        migrations.AlterModelOptions(
            name='courselevel',
            options={'verbose_name_plural': 'Course Level Table'},
        ),
        migrations.AlterModelOptions(
            name='coursematerial',
            options={'verbose_name_plural': 'Course Material'},
        ),
        migrations.AlterModelOptions(
            name='coursematerialstatus',
            options={'verbose_name_plural': 'Course Material Status'},
        ),
        migrations.AlterModelOptions(
            name='courserating',
            options={'verbose_name_plural': 'Course Rating Table'},
        ),
        migrations.AlterModelOptions(
            name='coursesubcategorydetails',
            options={'verbose_name_plural': 'Course Sub Category Table'},
        ),
        migrations.AlterModelOptions(
            name='coursetype',
            options={'verbose_name_plural': 'Course Type Table'},
        ),
        migrations.AlterModelOptions(
            name='eventad',
            options={'verbose_name_plural': 'EventAd Table'},
        ),
        migrations.AlterModelOptions(
            name='eventadenroll',
            options={'verbose_name_plural': 'Event Ad Enroll'},
        ),
        migrations.AlterModelOptions(
            name='eventadpaymentdetail',
            options={'verbose_name_plural': 'Event Ad Payment Detail'},
        ),
        migrations.AlterModelOptions(
            name='favouritecourse',
            options={'verbose_name_plural': 'Favourite Course'},
        ),
        migrations.AlterModelOptions(
            name='feetype',
            options={'verbose_name_plural': 'Fee Type Table'},
        ),
        migrations.AlterModelOptions(
            name='header_footercms',
            options={'verbose_name_plural': 'Header_FooterCMS'},
        ),
        migrations.AlterModelOptions(
            name='header_footercms_sv',
            options={'verbose_name_plural': 'Header_FooterCMS SV'},
        ),
        migrations.AlterModelOptions(
            name='homepagecms',
            options={'verbose_name_plural': 'Home Page'},
        ),
        migrations.AlterModelOptions(
            name='homepagecms_sv',
            options={'verbose_name_plural': 'Home Page SV'},
        ),
        migrations.AlterModelOptions(
            name='homepagecmsbanner',
            options={'verbose_name_plural': 'Home Page CMS Banner Table'},
        ),
        migrations.AlterModelOptions(
            name='homepagecmsbanner_sv',
            options={'verbose_name_plural': 'Home Page CMS Banner Table SV'},
        ),
        migrations.AlterModelOptions(
            name='homepagecmspartners',
            options={'verbose_name_plural': 'Home Page CMS Partners Table'},
        ),
        migrations.AlterModelOptions(
            name='homepagecmspartners_sv',
            options={'verbose_name_plural': 'Home Page CMS Partners Table SV'},
        ),
        migrations.AlterModelOptions(
            name='invoicedata',
            options={'verbose_name_plural': 'Invoice Data'},
        ),
        migrations.AlterModelOptions(
            name='invoicedataevent',
            options={'verbose_name_plural': 'Invoice Data Event'},
        ),
        migrations.AlterModelOptions(
            name='invoicevatcms',
            options={'verbose_name_plural': 'Invoice VAT Table'},
        ),
        migrations.AlterModelOptions(
            name='materialdocumentmaterial',
            options={'verbose_name_plural': 'Material Document Material'},
        ),
        migrations.AlterModelOptions(
            name='materialvideomaterial',
            options={'verbose_name_plural': 'Material Video Material'},
        ),
        migrations.AlterModelOptions(
            name='nonbuiltinusertoken',
            options={'verbose_name_plural': 'Non BuiltIn User Token'},
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'verbose_name_plural': 'Notification Table'},
        ),
        migrations.AlterModelOptions(
            name='privacypolicycms',
            options={'verbose_name_plural': 'Privacy Policy Page'},
        ),
        migrations.AlterModelOptions(
            name='privacypolicycms_sv',
            options={'verbose_name_plural': 'Privacy Policy Page SV'},
        ),
        migrations.AlterModelOptions(
            name='privacypolicycmssupplier',
            options={'verbose_name_plural': 'Privacy Policy Page Supplier'},
        ),
        migrations.AlterModelOptions(
            name='privacypolicycmssupplier_sv',
            options={'verbose_name_plural': 'Privacy Policy Page Supplier SV'},
        ),
        migrations.AlterModelOptions(
            name='recruitmentad',
            options={'verbose_name_plural': 'Recruitment Ad'},
        ),
        migrations.AlterModelOptions(
            name='supplierorganizationprofile',
            options={'verbose_name_plural': 'Supplier Organization Profile Table'},
        ),
        migrations.AlterModelOptions(
            name='supplierprofile',
            options={'verbose_name_plural': 'Supplier Profile'},
        ),
        migrations.AlterModelOptions(
            name='termsconditioncms',
            options={'verbose_name_plural': 'Terms & Condition Page'},
        ),
        migrations.AlterModelOptions(
            name='termsconditioncms_sv',
            options={'verbose_name_plural': 'Terms & Condition Page SV'},
        ),
        migrations.AlterModelOptions(
            name='termsconditioncmssupplier',
            options={'verbose_name_plural': 'Terms & Condition Page Supplier'},
        ),
        migrations.AlterModelOptions(
            name='termsconditioncmssupplier_sv',
            options={'verbose_name_plural': 'Terms & Condition Page Supplier SV'},
        ),
        migrations.AlterModelOptions(
            name='testinomialsdetails',
            options={'verbose_name_plural': 'Testinomials Details Table'},
        ),
        migrations.AlterModelOptions(
            name='testinomialsdetails_sv',
            options={'verbose_name_plural': 'Testinomials Details Table SV'},
        ),
        migrations.AlterModelOptions(
            name='userpaymentdetail',
            options={'verbose_name_plural': 'User Payment Detail'},
        ),
        migrations.AlterModelOptions(
            name='userpersonalprofile',
            options={'verbose_name_plural': 'User Personal Profile'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name_plural': 'User Eddi Profile'},
        ),
        migrations.AlterModelOptions(
            name='usersignup',
            options={'verbose_name_plural': 'User Signup Table'},
        ),
        migrations.AlterModelOptions(
            name='usertype',
            options={'verbose_name_plural': 'User Type Table'},
        ),
        migrations.AlterModelOptions(
            name='utl_status',
            options={'verbose_name_plural': 'Status Table'},
        ),
        migrations.AlterModelOptions(
            name='whatsoneddicms',
            options={'verbose_name_plural': "Whats'on Eddi CMS"},
        ),
        migrations.AlterModelOptions(
            name='whatsoneddicms_sv',
            options={'verbose_name_plural': "Whats'on Eddi CMS SV"},
        ),
    ]
