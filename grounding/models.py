from csc.conceptnet.models import (Language, Concept, Vote, ScoredModel,
UsefulAssertionManager)
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes import generic

class Color(models.Model):
    red = models.PositiveSmallIntegerField()
    green = models.PositiveSmallIntegerField()
    blue = models.PositiveSmallIntegerField()

    class Meta:
        db_table = 'conceptnet_color'

    def __unicode__(self):
        return u"rgb(%s,%s,%s)" % (self.red, self.green, self.blue)

class NotColorfulAssertion(models.Model, ScoredModel):
    objects = models.Manager()
    useful = UsefulAssertionManager()
    language = models.ForeignKey(Language)
    concept = models.ForeignKey(Concept)
    score = models.IntegerField(default=0)
    votes = generic.GenericRelation(Vote)

    class Meta:
        db_table = 'conceptnet_notcolorfulassertion'
        unique_together = ('concept', 'language')
        ordering = ['-score']

    def __unicode__(self):
        return u"NotColorfulAssertion(%s)" % (self.concept.text)

        def get_absolute_url(self):
            return '/%s/notcolorfulassertion/%s/' % (self.language.id, self.id)

class ColorAssertion(models.Model, ScoredModel):
    # Managers
    objects = models.Manager()
    useful = UsefulAssertionManager()
    language = models.ForeignKey(Language)
    concept = models.ForeignKey(Concept)
    color = models.ForeignKey(Color)
    score = models.IntegerField(default=0)
    votes = generic.GenericRelation(Vote)

    class Meta:
        unique_together = ('concept', 'color', 'language')
        ordering = ['-score']
        db_table = 'conceptnet_colorassertion'

    def __unicode__(self):
        #return "Assertion"
        return u"ColorAssertion(%s, %s)" % (self.concept.text, self.color)

    def get_absolute_url(self):
        return '/%s/colorassertion/%s/' % (self.language.id, self.id)

