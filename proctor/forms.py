from django import forms
from .models import Exam, Question
class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'start_time', 'end_time', 'duration', 'status']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'question_text', 'question_type',
            'choiceA', 'choiceB', 'choiceC', 'choiceD',
            'correct_answer', 'grade', 'question_media', 'keywords'
        ]

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        self.fields['question_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['question_text'].widget.attrs.update({'class': 'form-control', 'rows': 2})
        self.fields['correct_answer'].widget.attrs.update({'class': 'form-control'})

        for field_name in ['choiceA', 'choiceB', 'choiceC', 'choiceD', 'grade', 'keywords', 'question_media']:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        self.fields['grade'].help_text = "Enter the point value for this question"
