import datetime
from datetime import date

from django.contrib import messages
from django.core.files import File
from django.http import FileResponse
from experta import KnowledgeEngine, AS
from experta import Field, Fact
from experta import Rule
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect

from members.models import Diagnose, User


class Disease(Fact):
    wheezing = Field(str, mandatory=False)
    cough = Field(str, mandatory=False)
    coughingUpBlood = Field(str, mandatory=False)
    chestPain = Field(str, mandatory=False)
    rapidBreathing = Field(str, mandatory=False)
    rapidHeartbeat = Field(str, mandatory=False)
    smokingHistory = Field(str, mandatory=False)
    fever = Field(str, mandatory=False)
    ageGroup = Field(str, mandatory=False)
    gender = Field(str, mandatory=False)
    familyHistory = Field(str, mandatory=False)
    duration = Field(str, mandatory=False)
    shortnessOfBreath = Field(str, mandatory=False)
    # pass


def evaluate(facts, data):
    matchNo = 0
    for k, v in facts.items():
        try:
            if data[k] == v:
                matchNo += 1
        except:
            pass
        try:
            if isinstance(data[k], list) and any(symptom == facts for symptom in data):
                matchNo += 1
        except:
            pass

    percentage = matchNo / 9 * 100
    return round(percentage, 2)


class DiseaseDiagnosis(KnowledgeEngine):
    percentage = {}

    def __init__(self, post_data):
        super().__init__()
        self.post_data = post_data
        self.diagnosis_value = ""
        self.recommendations = ""
        self.pdf_file = None
        self.disease_title = None

    @Rule(Disease(wheezing="N", cough="dry", coughingUpBlood="N", chestPain="N",
                  rapidBreathing="N", rapidHeartbeat="N"))
    def pertussis_influenza_diagnosis(self):
        facts = {"wheezing": "N", "cough": "dry", "coughingUpBlood": "N", "chestPain": "N",
                 "rapidBreathing": "N", "rapidHeartbeat": "N"}
        self.percentage["pertussis and influenza"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Ймовірність даних захворювань складає "
                                + str(self.percentage["pertussis and influenza"]) + "%",
                                "Було встановлено, що ви хворієте на кашлюк або грип. "}
        with open("recommendations/pertussis_and_influenza.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Pertussis or Influenza"

    @Rule(Disease(wheezing="N", cough="dry", coughingUpBlood="N", chestPain="N",
                  rapidBreathing="N", rapidHeartbeat="Y"))
    def influenza_diagnosis1(self):
        facts = {"wheezing": "N", "cough": "dry", "coughingUpBlood": "N", "chestPain": "N",
                 "rapidBreathing": "N", "rapidHeartbeat": "Y"}
        self.percentage["influenza1"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на грип. ",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["influenza1"]) + "%"}
        with open("recommendations/influenza.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Influenza"

    @Rule(Disease(wheezing="N", cough="dry", coughingUpBlood="N", chestPain="N", rapidBreathing="Y"))
    def influenza_diagnosis2(self):
        print("You have influenza 2")
        facts = {"wheezing": "N", "cough": "dry", "coughingUpBlood": "N", "chestPain": "N",
                 "rapidBreathing": "Y", }
        self.percentage["influenza2"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на грип. ",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["influenza2"]) + "%"}
        with open("recommendations/influenza.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Influenza"

    @Rule(Disease(wheezing="N", cough="dry", coughingUpBlood="Y", chestPain="Y"))
    def influenza_diagnosis3(self):
        facts = {"wheezing": "N", "cough": "dry", "coughingUpBlood": "Y", "chestPain": "Y"}
        self.percentage["influenza3"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на грип. ",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["influenza3"]) + "%"}
        with open("recommendations/influenza.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Influenza"

    @Rule(Disease(wheezing="N", cough="dry", coughingUpBlood="Y"))
    def covid_diagnosis(self):
        facts = {"wheezing": "N", "cough": "dry", "coughingUpBlood": "Y"}
        self.percentage["covid"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на covid-19. ",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["covid"]) + "%"}
        with open("recommendations/covid.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Covid"

    @Rule(Disease(wheezing="N", cough="productive", smokingHistory="N", chestPain="N"))
    def croup_diagnosis(self):
        facts = {"wheezing": "N", "cough": "productive", "smokingHistory": "N", "chestPain": "N"}
        self.percentage["croup"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на Круп (або стенозуючий ларинготрахеобронхіт). ",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["croup"]) + "%"}
        with open("recommendations/croup.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Croup"

    @Rule(Disease(wheezing="N", cough="productive", smokingHistory="N", chestPain="Y"))
    def tuberculosis_diagnosis(self):
        facts = {"wheezing": "N", "cough": "productive", "smokingHistory": "N", "chestPain": "Y"}
        self.percentage["tuberculosis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на туберкульоз",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["tuberculosis"]) + "%"}
        with open("recommendations/tuberculosis.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Tuberculosis"

    @Rule(Disease(wheezing="N", cough="productive", smokingHistory="Y"))
    def rhinosinusitis_diagnosis(self):
        facts = {"wheezing": "N", "cough": "productive", "smokingHistory": "Y"}
        self.percentage["rhinosinusitis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на риносинусит",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["rhinosinusitis"]) + "%"}
        with open("recommendations/rhinosinusitis.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Rhinosinusitis"

    @Rule(Disease(wheezing="Y", smokingHistory="N", rapidBreathing="N", chestPain="N"))
    def common_cold_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "N", "rapidBreathing": "N", "chestPain": "N"}
        self.percentage["common_cold"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на простуду",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["common_cold"]) + "%"}
        with open("recommendations/common_cold.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Common Cold"

    @Rule(Disease(wheezing="Y", smokingHistory="N", rapidBreathing="N", chestPain="Y", coughingUpBlood="N"))
    def acute_bronchitis_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "N", "rapidBreathing": "N", "chestPain": "Y",
                 "coughingUpBlood": "N"}
        self.percentage["acute_bronchitis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на гострий бронхіт",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["acute_bronchitis"]) + "%"}
        with open("recommendations/acute_bronchitis.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Acute Bronchitis"

    @Rule(Disease(wheezing="Y", smokingHistory="N", rapidBreathing="N", chestPain="Y", coughingUpBlood="Y"))
    def bronchiectasis_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "N", "rapidBreathing": "N", "chestPain": "Y",
                 "coughingUpBlood": "Y"}
        self.percentage["bronchiectasis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на бронхоектатичну хворобу",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["bronchiectasis"]) + "%"}
        with open("recommendations/bronchiectasis.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Bronchiectasis"

    @Rule(Disease(wheezing="Y", smokingHistory="N", rapidBreathing="Y", cough="dry"))
    def asthma_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "N", "rapidBreathing": "Y", "cough": "dry"}
        self.percentage["asthma"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на астму",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["asthma"]) + "%"}
        with open("recommendations/asthma.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Asthma"

    @Rule(Disease(wheezing="Y", smokingHistory="N", rapidBreathing="Y", cough="productive", fever="N"))
    def asthma_and_cystic_fibrosis_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "N", "rapidBreathing": "Y", "cough": "productive", "fever": "N"}
        self.percentage["asthma_and_cystic_fibrosis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на астму або муковісцидоз.",
                                "Ймовірність даних захворювань складає "
                                + str(self.percentage["asthma_and_cystic_fibrosis"]) + "%"}
        with open("recommendations/asthma_and_cystic_fibrosis.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Asthma or Cystic Fibrosis"

    @Rule(Disease(wheezing="Y", smokingHistory="N", rapidBreathing="Y", cough="productive", fever="Y"))
    def cystic_fibrosis_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "N", "rapidBreathing": "Y", "cough": "productive", "fever": "Y"}
        self.percentage["cystic_fibrosis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на муковісцидоз.",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["cystic_fibrosis"]) + "%"}
        with open("recommendations/cystic_fibrosis.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Cystic Fibrosis"

    @Rule(Disease(wheezing="Y", smokingHistory="Y", chestPain="N", cough="dry"))
    def bronchiolitis_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "Y", "chestPain": "N", "cough": "dry"}
        self.percentage["bronchiolitis"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на бронхіоліт.",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["bronchiolitis"]) + "%"}
        with open("recommendations/bronchiolitis_elder.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Bronchiolitis"

    @Rule(Disease(wheezing="Y", smokingHistory="Y", chestPain="N", cough="productive"))
    def copd_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "Y", "chestPain": "N", "cough": "productive"}
        self.percentage["copd"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на ХОЗЛ(хронічне обстуктивне захворювання легень).",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["copd"]) + "%"}
        with open("recommendations/copd.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Copd"

    @Rule(Disease(wheezing="Y", smokingHistory="Y", chestPain="Y", cough="dry", coughingUpBlood="N"))
    def occupational_lung_diseases_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "Y", "chestPain": "Y", "cough": "dry", "coughingUpBlood": "N"}
        self.percentage["occupational_lung_diseases"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на професійне захворювання легень.",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["occupational_lung_diseases"]) + "%"}
        with open("recommendations/occupational_lung_diseases.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Occupational Lung Diseases"

    @Rule(Disease(wheezing="Y", smokingHistory="Y", chestPain="Y", cough="productive", coughingUpBlood="N"))
    def pneumonia_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "Y", "chestPain": "Y", "cough": "productive",
                 "coughingUpBlood": "N"}
        self.percentage["pneumonia"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на пневмонію.",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["pneumonia"]) + "%"}
        with open("recommendations/pneumonia.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Pneumonia"

    @Rule(Disease(wheezing="Y", smokingHistory="Y",
                  chestPain="Y", coughingUpBlood="Y"))
    def lung_cancer_diagnosis(self):
        facts = {"wheezing": "Y", "smokingHistory": "Y", "chestPain": "Y", "coughingUpBlood": "Y"}
        self.percentage["lung cancer"] = evaluate(facts, self.post_data)
        self.diagnosis_value = {"Було встановлено, що ви хворієте на рак легень.",
                                "Ймовірність даного захворювання складає "
                                + str(self.percentage["lung cancer"]) + "%"}

        with open("recommendations/lung_cancer.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Lung Cancer"

    @Rule(AS.fact << Disease())
    def default_diagnosis(self, fact):
        self.diagnosis_value = "Згідно із вашими симптомами не було встановлено діагноз. " \
                               "Рекомендуємо для впевненості в тому, що ви здорові пройти консультацію у лікаря"
        with open("recommendations/unknown.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
        self.recommendations = [line.rstrip('\n') + '\n' for line in lines]
        self.disease_title = "Unknown"

    def get_diagnosis_value(self):
        return self.diagnosis_value

    def get_disease_title(self):
        return self.disease_title

    def get_recommendation(self):
        return self.recommendations

    def get_pdf(self):
        return self.pdf_file


def MainForm(request):
    return render(request, 'expert_form.html')


def diagnose(request):
    if request.POST["wheezing"] == "" or request.POST["cough"] == "" or request.POST["coughingUpBlood"] == "" \
            or request.POST["chestPain"] == "" or request.POST["rapidBreathing"] == "" or request.POST["fever"] == "" \
            or request.POST["smokingHistory"] == "" \
            or request.POST["shortnessOfBreath"] == "" or request.POST["rapidHeartbeat"] == "":
        messages.error(request, "Заповніть усі поля симптомів для розширеного діагностування.")
        return redirect('/')

    wheezing = request.POST["wheezing"]
    cough = request.POST["cough"]
    coughingUpBlood = request.POST["coughingUpBlood"]
    chestPain = request.POST["chestPain"]
    rapidBreathing = request.POST["rapidBreathing"]
    fever = request.POST["fever"]
    smokingHistory = request.POST["smokingHistory"]
    user = User.objects.get(username=request.user.username)
    ageGroup = "adult" if datetime.date.today().year - user.birthday.year >= 16 else "child"
    shortnessOfBreath = request.POST["shortnessOfBreath"]
    rapidHeartbeat = request.POST["rapidHeartbeat"]
    gender = user.gender
    post_data = {'wheezing': wheezing, 'cough': cough,
                 'chestPain': chestPain,
                 'coughingUpBlood': coughingUpBlood,
                 'rapidBreathing': rapidBreathing, "fever": fever, "smokingHistory": smokingHistory,
                 "ageGroup": ageGroup, "shortnessOfBreath": shortnessOfBreath,
                 "rapidHeartbeat": rapidHeartbeat, "gender": gender}
    engine = DiseaseDiagnosis(post_data)
    engine.reset()
    engine.declare(Disease(wheezing=wheezing, cough=cough,
                           coughingUpBlood=coughingUpBlood,
                           chestPain=chestPain, rapidBreathing=rapidBreathing,
                           fever=fever, smokingHistory=smokingHistory,
                           ageGroup=ageGroup,
                           shortnessOfBreath=shortnessOfBreath,
                           rapidHeartbeat=rapidHeartbeat,
                           gender=gender))
    engine.run()

    pdf_file = "recommendation.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    font_path = "fonts/Arial Unicode MS.ttf"
    font_name = "Arial"
    pdfmetrics.registerFont(TTFont(font_name, font_path))
    generate_pdf(c, engine, font_name, request)

    response = FileResponse(open(pdf_file, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recommendation.pdf"'

    save_diagnose(pdf_file, request, engine.get_disease_title())

    return response


def save_diagnose(pdf_file, request, disease_title):
    saved_diagnose = Diagnose(user=request.user)
    saved_diagnose.title = disease_title
    with open(pdf_file, "rb") as pdf_file:
        saved_diagnose.pdf_file.save("generated_pdf.pdf", File(pdf_file))
    saved_diagnose.save()


def generate_pdf(c, engine, font_name, request):
    frame_x = 20
    frame_y = 10
    frame_width = 565
    frame_height = 760
    logo_width = 1.35 * inch
    logo_height = 0.75 * inch
    logo_x = 0.5 * inch
    logo_y = letter[1] - (0.5 * inch) - logo_height
    logo_path = 'media/logos.png'
    c.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height)
    company_name = "Diagnostic System of Lung Diseases"
    current_date = date.today().strftime("%B %d, %Y")
    patient_name = request.user.first_name + ' ' + request.user.last_name
    email = 'Email: ' + request.user.email
    header_x = logo_x + logo_width + 0.25 * inch
    header_y = logo_y + 0.5 * inch
    header_font_size = 10
    c.setFont(font_name, header_font_size)
    c.drawString(header_x, header_y, company_name)
    c.drawString(header_x, header_y - header_font_size, current_date)
    c.drawString(header_x, header_y - 2 * header_font_size, "Пацієнт: " + patient_name)
    c.drawString(header_x, header_y - 3 * header_font_size, email)
    c.rect(frame_x, frame_y, frame_width, frame_height, stroke=True, fill=False)
    c.setFont(font_name, 18)
    c.setFillColor("#085D6B")
    c.drawString(frame_x + 200, frame_y + frame_height - 100, "Попередній діагноз:")
    c.setFont(font_name, 10)
    c.setFillColor("black")
    rect_x = frame_x + 130
    rect_y = frame_y + frame_height - 180
    rect_width = 300
    rect_height = 60
    rect_fill_color = "#f0776e"  # Red color
    c.setFont(font_name, 12)
    c.setFillColor(rect_fill_color)
    c.rect(rect_x, rect_y, rect_width, rect_height, fill=True)
    c.setFillColor("black")
    dif = 20
    for diagnose_val in engine.get_diagnosis_value():
        y = frame_y + frame_height - 120 - dif
        c.drawString(rect_x + 10, y, diagnose_val)
        dif += 20
    c.setFont(font_name, 18)
    c.setFillColor("#085D6B")
    c.drawString(frame_x + 220, frame_y + frame_height - 200, "Рекомендації:")
    c.setFont(font_name, 10)
    dif = 220
    c.setFillColor("black")
    for recommendation in engine.get_recommendation():
        if recommendation.startswith('●'):
            line_x1 = frame_x
            line_x2 = frame_x + 565.5
            line_y = frame_y + frame_height - dif + 12

            line_color = "black"
            line_width = 1

            c.setStrokeColor(line_color)
            c.setLineWidth(line_width)
            c.line(line_x1, line_y, line_x2, line_y)
        y = frame_y + frame_height - dif
        c.drawString(frame_x + 10, y, recommendation[:-1])
        dif += 20
    c.setFont(font_name, 18)
    c.setFillColor("#ab1105")
    c.drawString(frame_x + 35, frame_y + frame_height - 755, "САМОЛІКУВАННЯ ШКІДЛИВЕ ДЛЯ ВАШОГО ЗДОРОВ'Я!")
    c.save()
