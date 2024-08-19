comp_mcq = """Write a comprehension or definition exercise in {language} that is based on the following text:
----
{StoryBlock}
----

Follow the rules:

1. The exercise must have three answer options.
2. The exercise must be fewer than 75 characters.
3. The exercise must be written in {cefr} CEFR level {language}.
4. Provide the correct answer.

Go!"""


comp_tf = """Write a true/false comprehension or definition exercise in {language} that is based on the following text:
----
{StoryBlock}
----

Follow the rules:

1. The exercise must have two answer options (true/false, yes/no, etc).
2. The exercise must be fewer than 75 characters.
3. The exercise must be written in {cefr} CEFR level {language}.
4. Provide the correct answer.

Go!"""


comp_listen = """Write a listening comprehension exercise in {language} by providing possible interpretations of the the last part of the following text if it were heard audibly and not read:
----
{StoryBlock}
----

Follow the rules:

1. The exercise must have three answer options.
2. The exercise must be written in {cefr} CEFR level {language}.
3. The correct answer must be the exact same as the last part of the text.
4. The three answer options must be similar.

Go!"""

pronounce_rep = """Select a very short section of the following text for the user to read aloud:
----
{StoryBlock}
----

Follow the rules:

1. The exercise must be written for {cefr} CEFR level {language}.
2. The chosen text must be shorter than or equal to one sentence.

Go!"""

pronounce_deaf = """Select the final part of the following text for the user to read aloud:
----
{StoryBlock}
----

Follow the rules:

1. The exercise must be written for {cefr} CEFR level {language}.
2. The chosen text must be shorter than or equal to the final sentence.
3. The chosen text must be at the end of the text.

Go!"""


speak_question = """Ask an open-ended and simple short answer question based on the following text in {language}:
----
{StoryBlock}
----

Follow the rules:

1. The exercise must be written for {cefr} CEFR level {language}.
2. The question must be related to the story or the opinion of the respondent to the story.

Go!"""

interact = """Ask an open-ended and short question based on the following text in {language}:
----
{previous StoryBlock}
----

Follow the rules:

1. The exercise must be written for {cefr} CEFR level {language}.
2. The question must be related to the story or the opinion of the respondent to the story.

Go!
"""
