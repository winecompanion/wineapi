from django.db import models

# Create your models here.

# missing fields attributes
class Reservation(models.Model):

    id_reservation = models.AutoField(primary_key=True)
    reservation_creation_date_time = models.DateTimeField()
    comments = models.TextField()
    total_amount = models.FloatField()
    kids_number = models.IntegerField()
    teenagers_number = models.IntegerField()
    adults_number = models.IntegerField()

    state_reservation = models.ForeignKey(StateReservation)

    def __str__(self):
        return str(self.id_reservation)


class StateReservation(models.Model):
    
    id_state_reservation = models.AutoField(primary_key=True)
    state_change_date_time = models.DateTimeField()
    comments = models.TextField()
    
    reservation_state = models.ForeignKey(ReservationState)

    def __str__(self):
        return str(self.id_state_reservation)


class ReservationState(models.Model):
    id_reservation_state = models.AutoField()
    reservation_state_name = models.CharField()

    def __str__(self):
        return str(self.id_reservation_state)


class EventOcurrence(models.Model)
    id_event_ocurrence = models.DateTimeField()
    canceled = models.DateTimeField()
    ocurrence_end_date_time = models.DateTimeField()
    ocurrence_start_date_time = models.DateTimeField()
    hour_duration = models.TimeField()
    available_capacity = models.IntegerField()
    
    def __str__(self):
        return str(self.id_event_ocurrence)


