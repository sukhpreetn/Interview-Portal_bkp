# Generated by Django 3.0.3 on 2020-03-02 21:37

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('c_comment', models.CharField(max_length=100)),
                ('c_new_quest', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('q_subject', models.CharField(max_length=40)),
                ('q_cat', models.CharField(max_length=40)),
                ('q_rank', models.CharField(max_length=20)),
                ('q_text', models.CharField(default='', max_length=700)),
                ('q_option1', models.CharField(default='', max_length=200)),
                ('q_option2', models.CharField(default='', max_length=200)),
                ('q_option3', models.CharField(default='', max_length=200)),
                ('q_option4', models.CharField(default='', max_length=200)),
                ('q_answer', models.CharField(max_length=20)),
                ('q_ask_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('no_times_ques_served', models.IntegerField()),
                ('no_times_anwered_correctly', models.IntegerField()),
                ('no_times_anwered_incorrectly', models.IntegerField()),
                ('difficulty_score', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ans_option', models.CharField(max_length=255)),
                ('is_correct', models.BooleanField(default=False)),
                ('ans_time', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AIP.Question')),
            ],
        ),
    ]
