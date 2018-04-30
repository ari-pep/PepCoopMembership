# -*- coding: utf-8 -*-


def make_mtype_email_body(input, the_url):
    if input.locale == 'de':
        body = u'''Hallo {0} {1},

gemeinsam mit Dir freuen wir uns auf die erste Generalversammlung der C3S SCE
am 23. August, um 14:00 Uhr im Millowitsch-Theater in Köln. Details dazu
erhältst Du in Kürze in einer separaten Einladung.

Von Dir fehlt uns aktuell noch eine Angabe dazu, ob Du nutzendes (ordentliches)
Mitglied oder investierendes (nicht-ordentliches) Mitglied werden möchtest bzw.
kannst. Gemäß der Satzung der C3S SCE [1] müssen ordentliche Mitglieder in der
Lage sein, uns mindestes drei eigene Musikwerke zur Verwertung zu übertragen.
In der Generalversammlung sind zudem ausschließlich ordentliche Mitglieder
stimmberechtigt. Außerdem ist es für uns wichtig zu wissen, ob Du bereits
Mitglied einer anderen Verwertungsgesellschaft in Deutschland oder auch im
Ausland bist.

Um es so einfach wie möglich zu gestalten, geben wir Dir einen individuellen
Link zu einer Webpage, auf der Du uns mit wenigen Klicks mit Deinen
Informationen versorgen kannst:

  {2}

Dort findest Du alle relevanten Hinweise und Erklärungen, die Dir die Wahl
erleichtern. Bleiben dennoch Fragen, schreibe uns bitte unter members-admin@pep.coop

Bitte ergänze Deine Angaben bis zum 10. Juli 2014. Erhalten wir bis zum 10.
Juli keine Angaben von Dir, gehen wir davon aus, dass Du investierendes
Mitglied (ohne Stimmrecht) werden möchtest.


Nicht vergessen, please spread the word: Wir suchen ständig aktive Supporter
und Neumitglieder. Wer als bestehendes Mitglied seine Anteile aufstocken will,
muss momentan noch das Formular für Neumitglieder nutzen [2]. Wir führen die
Daten anschließend zusammen. Wer uns dagegen monatlich helfen möchte, unsere
laufenden Kosten zu bestreiten, kann uns unter dem Motto "I sustain C3S" mit
regelmäßigen, kleinen Beiträgen unterstützen [3].

Genießt den Sommer, und freut Euch mit uns auf eine faire Bezahlung für Musiker
mit der C3S!


Viele Grüße

Das Team der C3S



[1] https://archive.c3s.cc/aktuell/legal/C3S_SCE_de.pdf

[2] https://yes.c3s.cc

[3] https://sustain.c3s.cc

++++++++++++++++++ I sustain C3S! ++++++++++++++++++
+++ Dein Beitrag zu fairer Bezahlung für Musiker +++
+++            https://sustain.c3s.cc            +++
+++                                              +++
+++     Support fair remuneration for artists    +++
+++          https://sustain.c3s.cc/?en          +++
++++++++++++++++++++++++++++++++++++++++++++++++++++
'''.format(
    input.firstname,  # noqa
    input.lastname,
    the_url,
)
    else:
        body = u'''Hello {0} {1},

together with you we are happily awaiting the first general assembly of p≡p coop SCE
on August 23rd, at 2 pm in the Millowitsch Theater in Cologne. You will soon
receive the details in a separate invitation.

We still require your information about whether you want to become an active
(full) member or a supporting (associate) member. According to the statutes of
p≡p coop SCE [1], full members must be able to assign at least three works of music
created by them to us for utilization. Only full members are entitled to vote
in the general assembly. It is also important for us to know whether you
already are a member of another collecting society in Germany or abroad.

In order to keep things as easy as possible for you, we give you an individual
link to a website where you can enter your data with just a few clicks:

  {2}

You will find all relevant information and explanations that enable you to make
the right choice. If you still have questions, please write to us: members-admin@pep.coop

Please complete your data until July 10th, 2014. If we do not receive your data
until then, we will set your membership status to be 'investing' (no vote) as
opposed to 'full' (eligible to vote).

And please don't forget to spread the word! We are still looking for active
supporters and new members. If you want to subscribe to additional shares,
you have to use the form for new members [2]. We will bring the data together
later.

If you want to make a regular monthly contribution to help us covering our
expenses, you can do so under the motto "I sustain C3S" [3].

Enjoy the summer and look forward, as we do,
to a fair pay for musicians with C3S!


Best wishes

Your p≡p coop team



[1] https://archive.c3s.cc/aktuell/legal/C3S_SCE_en.pdf

[2] https://yes.c3s.cc

[3] https://sustain.c3s.cc

++++++++++++++++++ I sustain C3S! ++++++++++++++++++
+++ Dein Beitrag zu fairer Bezahlung für Musiker +++
+++            https://sustain.c3s.cc            +++
+++                                              +++
+++     Support fair remuneration for artists    +++
+++          https://sustain.c3s.cc/?en          +++
++++++++++++++++++++++++++++++++++++++++++++++++++++
'''.format(
    input.firstname,  # noqa
    input.lastname,
    the_url,
)
    return body
