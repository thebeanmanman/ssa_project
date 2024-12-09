from django.db import models
from django.contrib.auth.models import User
import math

class Group(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(User, related_name='admin_groups', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='group_memberships', blank=True)
    invited_users = models.ManyToManyField(User, related_name='pending_invitations', blank=True)

    def __str__(self):
        return self.name
    
class GroupJoinRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='join_requests')
    is_approved = models.BooleanField(default=False)
    votes = models.ManyToManyField(User, related_name='votes', blank=True)  # Tracks users who voted
    created_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who posted the comment
    group = models.ForeignKey(Group, related_name='comments', on_delete=models.CASCADE)  # Group associated with the comment
    content = models.TextField()  # The comment content
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the comment was posted
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the latest update

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}..."  # Show only first 20 chars for preview
    
class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    total_spend = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending')  # Can be 'Pending' or 'Active'
    group = models.ForeignKey(Group, related_name='events', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='event_memberships', blank=True)

    def calculate_share(self):
        members_count = self.members.count()
        if members_count == 0:
            return 0
        return round(self.total_spend / members_count,2) # Calculates each share of a member by dividing the total spend by member count. Then it is rounded to 2DP to ensure no errors in transactions 
        
    def calculate_extra_share(self): # Calculates the share that would be given to the user if they joined the event. This allows for checking if the user has enough funds to join.
        members_count = self.members.count()+1 # Accounts for the extra member in the group
        return round(self.total_spend / members_count,2) # Gets the new share price by using the extra member
    def check_status(self):
        """ Check if all members' max spend can cover the event. """
        share = self.calculate_share()
        for member in self.members.all():
            if member.profile.max_spend < share:
                return False
        return True
    
    def check_balances(self): # Checks if all members balance can cover the event cost
        share = self.calculate_share() # Calculates the share for the event
        for member in self.members.all(): # Loops through all the members in the event
            if member.profile.balance < share: # Checks if the members balance is less than the share
                return False # Returns false if one of the members balance is less than the share
        return True # Returns true if all members' balance can cover the event