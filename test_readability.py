"""Acceptance tests for the Readability exercise.

Each test runs your program as a whole, exactly as a user would: it writes
a text in a file, gives the name of this file on the command line, then
checks what your program prints and tries to explain what is wrong.

Run the tests from the exercise folder with:

    python test_readability.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

EXERCISE_DIR = Path(__file__).resolve().parent
SCRIPT = "readability.py"
USAGE = "Usage: python readability.py filename"
TIMEOUT = 5  # seconds

# Each test case: (what is checked, text written in the file).
# The expected grade is computed by the grade_line() function below.
CASES = [
    ("Before Grade 1 (a very simple text)",
     "One fish. Two fish! Red fish? Blue fish."),
    ("Grade 1 (and not 'Before Grade 1')",
     "We each have genes. Genes are made of DNA. They tell your body how "
     "to grow. You got half of your genes from your mom and half from "
     "your dad."),
    ("Grade 2",
     "Would you like them here or there? I would not like them here or "
     "there. I would not like them anywhere."),
    ("Grade 3",
     "Congratulations! Today is your day. You're off to Great Places! "
     "You're off and away!"),
    ("Grade 5",
     "Harry Potter was a highly unusual boy in many ways. For one thing, "
     "he hated the summer holidays more than any other time of year. For "
     "another, he really wanted to do his homework, but was forced to do "
     "it in secret, in the dead of the night. And he also happened to be "
     "a wizard."),
    ("Grade 6",
     "Sophie couldn't sleep. A brilliant moonbeam was slanting through a "
     "gap in the curtains. It was shining right on to her pillow. The "
     "other children in the dormitory had been asleep for hours. Sophie "
     "closed her eyes and lay quite still. She tried every hard to doze "
     "off. It was no good. The moonbeam was like a silver blade slicing "
     "through the room on to her face."),
    ("Grade 7",
     "In my younger and more vulnerable years my father gave me some "
     "advice that I've been turning over in my mind ever since."),
    ("Grade 8 (a quotation inside the text)",
     "Alice was beginning to get very tired of sitting by her sister on "
     "the bank, and of having nothing to do: once or twice she had peeped "
     "into the book her sister was reading, but it had no pictures or "
     "conversations in it, \"and what is the use of a book,\" thought "
     "Alice \"without pictures or conversation?\""),
    ("Grade 8 (a hyphenated word counts as one word)",
     "When he was nearly thirteen, my brother Jem got his arm badly broken "
     "at the elbow. When it healed, and Jem's fears of never being able to "
     "play football were assuaged, he was seldom self-conscious about his "
     "injury. His left arm was somewhat shorter than his right; when he "
     "stood or walked, the back of his hand was at right angles to his "
     "body, his thumb parallel to his thigh."),
    ("Grade 9",
     "There are more things in Heaven and Earth, Horatio, than are dreamt "
     "of in your philosophy."),
    ("Grade 10",
     "It was a bright cold day in April, and the clocks were striking "
     "thirteen. Winston Smith, his chin nuzzled into his breast in an "
     "effort to escape the vile wind, slipped quickly through the glass "
     "doors of Victory Mansions, though not quickly enough to prevent a "
     "swirl of gritty dust from entering along with him."),
    ("Grade 11 (index 10.52, rounded to 11)",
     "Morning-room in Algernon's flat in Half-Moon Street. The room is "
     "luxuriously and artistically furnished. The sound of a piano is "
     "heard in the adjoining room."),
    ("Grade 12",
     "A squat grey building of only thirty-four storeys. Over the main "
     "entrance the words, Central London Hatchery and Conditioning Centre, "
     "and, in a shield, the World State's motto, Community, Identity, "
     "Stability. The enormous room on the ground floor faced towards the "
     "north. Cold for all the summer beyond the panes, for all the "
     "tropical heat of the room itself, a harsh thin light glared through "
     "the windows, hungrily seeking some draped lay figure, some pallid "
     "shape of academic goose-flesh, but finding only the glass and nickel "
     "and bleakly shining porcelain of a laboratory. Wintriness responded "
     "to wintriness. The overalls of the workers were white, their hands "
     "gloved with a pale corpse-coloured rubber. The light was frozen, "
     "dead, a ghost. Only from the yellow barrels of the microscopes did "
     "it borrow a certain rich and living substance, lying along the "
     "polished tubes like butter, streak after luscious streak in long "
     "recession down the work tables."),
    ("Grade 16+ (index 16.41, rounded to 16)",
     "The surgical stimulus to which we were both subjected has resulted "
     "in ALGERNON an intensification and acceleration of all mental "
     "processes. The unforeseen development, which I have taken the "
     "liberty of calling the Algernon-Gordon Effect, is the logical "
     "extension of the entire intelligence speed-up. The hypothesis here "
     "proven may be described simply in the following terms: Artifically "
     "increased intelligence deteriorates at a rate of time directly "
     "proportional to the quantity of the increase."),
    ("Grade 16+ (index 18.15)",
     "A large class of computational problems involve the determination "
     "of properties of graphs, digraphs, integers, arrays of integers, "
     "finite families of finite sets, boolean formulas and elements of "
     "other countable domains."),
    ("digits are not letters",
     "In 2003, the Human Genome Project published about 3 billion base "
     "pairs of DNA. It took 13 years and cost nearly 3 billion dollars."),
    ("a text on several lines (a newline also separates two words)",
     "Bacteria are tiny living things.\n"
     "Most of them are harmless,\n"
     "and some of them even help us\n"
     "to digest our food.\n"
     "Others can make us sick.\n"
     "That is why we wash our hands."),
    ("two spaces after each sentence",
     "Proteins fold.  Some of them fold badly.  Misfolded proteins can "
     "stick together and form clumps in the brain.  Chaperone proteins "
     "help the other proteins to fold correctly."),
]

# Text files given with the exercise: (what is checked, file name).
FILE_CASES = [
    ("file cells.txt", "cells.txt"),
    ("file evolution.txt", "evolution.txt"),
    ("file genome.txt", "genome.txt"),
]

# Invalid command lines: (what is checked, arguments).
# The program must print the usage message and stop.
USAGE_CASES = [
    ("no file name", []),
    ("two file names", ["cells.txt", "genome.txt"]),
]

# Frequent mistakes: (parameters of grade_line() reproducing the mistake,
# explanation). After all the tests, the explanations of the mistakes
# that give exactly the results printed by the program are shown.
MISTAKES = [
    ({"letters": "alnum"},
     "Digits seem to be counted as letters: use str.isalpha(), not "
     "str.isalnum()."),
    ({"letters": "not_space"},
     "Punctuation marks seem to be counted as letters: count only the "
     "characters for which str.isalpha() is True."),
    ({"letters": "all"},
     "Every character (spaces, punctuation...) seems to be counted as a "
     "letter: count only the characters for which str.isalpha() is True."),
    ({"words": "spaces"},
     "Your program seems to count the words as the number of spaces + 1. "
     "It is wrong when two words are separated by a newline or by several "
     "spaces: str.split() (without argument) cuts a text on any "
     "whitespace."),
    ({"first_line": True},
     "Your program seems to read only the first line of the file: "
     "file.read() reads the whole file at once."),
    ({"sentences": "."},
     "Only '.' seems to end a sentence: '!' and '?' end a sentence too."),
    ({"rounding": "int"},
     "The grade seems truncated instead of rounded: int(10.52) is 10 "
     "but round(10.52) is 11."),
    ({"top": "none"},
     "When the grade is 16 or more, your program should print "
     "'Grade 16+' instead of the grade."),
    ({"top": ">"},
     "When the grade is exactly 16, your program should print "
     "'Grade 16+': check your comparison (> versus >=)."),
    ({"bottom": "<="},
     "When the grade is exactly 1, your program should print 'Grade 1': "
     "check your comparison (< versus <=)."),
    ({"division": "//"},
     "Your program seems to use the integer division //: L and S must be "
     "computed with the true division / (nb_letters * 100 / nb_words)."),
]

# Text typed if the program asks something (it should not).
UNEXPECTED_INPUT = ""


# ---------------------------------------------------------------------------
# Expected results
# ---------------------------------------------------------------------------

def count(text, letters="alpha", words="split", sentences=".!?",
          first_line=False):
    """Return (number of letters, words, sentences) of a text.

    The optional parameters reproduce frequent mistakes:
    - letters: "alpha" (right), "alnum" (digits counted), "not_space"
      (punctuation counted), "all" (every character counted);
    - words: "split" (right) or "spaces" (number of spaces + 1);
    - sentences: the characters that end a sentence;
    - first_line: if True, only the first line of the text is read.
    """
    if first_line:
        text = text.split("\n")[0]
    nb_letters = 0
    nb_sentences = 0
    for char in text:
        if letters == "alpha" and char.isalpha():
            nb_letters += 1
        elif letters == "alnum" and char.isalnum():
            nb_letters += 1
        elif letters == "not_space" and not char.isspace():
            nb_letters += 1
        elif letters == "all":
            nb_letters += 1
        if char in sentences:
            nb_sentences += 1
    if words == "spaces":
        nb_words = text.strip("\n").count(" ") + 1
    else:
        nb_words = len(text.split())
    return nb_letters, nb_words, nb_sentences


def coleman_liau(nb_letters, nb_words, nb_sentences, division="/"):
    """Return (L, S, index) of the Coleman-Liau formula."""
    if division == "//":
        avg_letters = nb_letters * 100 // nb_words
        avg_sentences = nb_sentences * 100 // nb_words
    else:
        avg_letters = nb_letters * 100 / nb_words
        avg_sentences = nb_sentences * 100 / nb_words
    index = 0.0588 * avg_letters - 0.296 * avg_sentences - 15.8
    return avg_letters, avg_sentences, index


def grade_line(text, rounding="round", top=">=", bottom="<",
               division="/", **count_parameters):
    """Return the line the program should print for the text.

    The optional parameters reproduce frequent mistakes (see count()):
    - rounding: "round" (right) or "int" (truncated);
    - top: ">=" (right), ">" or "none" (never) to print "Grade 16+";
    - bottom: "<" (right) or "<=" to print "Before Grade 1";
    - division: "/" (right) or "//".
    """
    _, _, index = coleman_liau(*count(text, **count_parameters),
                               division=division)
    grade = round(index) if rounding == "round" else int(index)
    if grade < 1 or (bottom == "<=" and grade == 1):
        return "Before Grade 1"
    if top != "none" and (grade > 16 or (top == ">=" and grade == 16)):
        return "Grade 16+"
    return f"Grade {grade}"


# ---------------------------------------------------------------------------
# Running the student's program
# ---------------------------------------------------------------------------

def run_program(arguments):
    """Run the program with the arguments.

    Return (stdout, stderr, return code), or None if the program
    did not stop in time.
    """
    try:
        # sys.executable is the Python running the tests,
        # so "python" vs "python3" does not matter.
        result = subprocess.run(
            [sys.executable, SCRIPT] + arguments,
            input=UNEXPECTED_INPUT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=EXERCISE_DIR,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"),
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None
    stdout = result.stdout.replace("\r\n", "\n")
    stderr = result.stderr.replace("\r\n", "\n").strip()
    return stdout, stderr, result.returncode


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def show(text):
    """Indent the lines of a text, with each line between quotes."""
    lines = text.splitlines()
    if not lines:
        return "    (nothing)"
    return "\n".join(f"    {line!r}" for line in lines)


def last_lines(text, nb_lines=4):
    """Return the last lines of a text, indented."""
    lines = text.split("\n")[-nb_lines:]
    return "\n".join("    " + line for line in lines)


def plural(number, word):
    """Return e.g. '1 sentence' or '3 sentences'."""
    return f"{number} {word}" if number == 1 else f"{number} {word}s"


def short(text, length=70):
    """Return the beginning of a text on one line."""
    text = " ".join(text.split())
    if len(text) <= length:
        return repr(text)
    return repr(text[:length] + "...")


def explain_expected(text):
    """Explain how the expected grade is computed for the text."""
    nb_letters, nb_words, nb_sentences = count(text)
    avg_letters, avg_sentences, index = coleman_liau(
        nb_letters, nb_words, nb_sentences)
    return (f"The text has {plural(nb_letters, 'letter')}, "
            f"{plural(nb_words, 'word')} and "
            f"{plural(nb_sentences, 'sentence')}, so L = {avg_letters:.2f}, "
            f"S = {avg_sentences:.2f} and index = {index:.2f}, "
            f"rounded to {round(index)}.")


def explain_crash(stderr):
    """Explain the most common errors that make the program crash."""
    message = f"Your program crashed:\n{last_lines(stderr)}"
    if "EOFError" in stderr:
        message += ("\nYour program asks the user something with input(). "
                    "It should not: the file name is given on the command "
                    "line, in sys.argv[1].")
    elif "IndexError" in stderr and "argv" in stderr:
        message += ("\nsys.argv does not have as many elements as you "
                    "think: check len(sys.argv) before using sys.argv[1].")
    elif "FileNotFoundError" in stderr:
        message += ("\nYour program tried to open a file that does not "
                    "exist: open the file whose name is in sys.argv[1].")
    elif "ZeroDivisionError" in stderr:
        message += ("\nYour program divided by zero: the number of words "
                    "should never be 0 for these texts. Check how you "
                    "count the words.")
    elif "UnicodeDecodeError" in stderr:
        message += ("\nThe file could not be read: open it with "
                    "open(filename, encoding='utf-8').")
    return message


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_usage(arguments):
    """Check that an invalid command line prints the usage message only.

    Return None if the test passes, else an error message.
    """
    result = run_program(arguments)
    if result is None:
        return "Your program did not stop (infinite loop?)."
    stdout, stderr, _ = result
    if stdout == USAGE + "\n" and stderr == "":
        return None
    # sys.exit("Usage: ...") writes the message on stderr: it is accepted too.
    if stdout == "" and stderr == USAGE:
        return None

    lines = stdout.splitlines()
    printed = "Your program printed:\n" + show(stdout)
    if "Traceback" in stderr and USAGE in stdout:
        return (f"Your program printed the usage message, but then it went "
                f"on and crashed. It should stop right after the usage "
                f"message (e.g. with sys.exit()).\n{printed}\n"
                f"{explain_crash(stderr)}")
    if "Traceback" in stderr:
        return explain_crash(stderr)
    if any(line.strip() == USAGE for line in lines):
        if len(lines) > 1:
            return (f"Your program printed the usage message, but then it "
                    f"went on. It should stop right after the usage message "
                    f"(e.g. with sys.exit()).\n{printed}")
        return (f"Your program should print only {USAGE!r}, nothing else "
                f"(not even spaces).\n{printed}")
    if any(line.strip().lower() == USAGE.lower() for line in lines):
        return (f"Check the case and the spelling: the message must be "
                f"exactly {USAGE!r}.\n{printed}")
    if any(line.startswith("Usage") for line in lines):
        return f"The usage message must be exactly {USAGE!r}.\n{printed}"
    if any(line.startswith(("Grade", "Before")) for line in lines):
        return (f"There must be exactly one file name on the command line: "
                f"your program should print {USAGE!r}.\n{printed}")
    return f"Your program should print {USAGE!r}.\n{printed}"


def check_line(stdout):
    """Check that the program printed a single valid line.

    Return (error message or None, line printed or None if not valid).
    """
    lines = stdout.splitlines()
    printed = "Your program printed:\n" + show(stdout)
    if not lines:
        return "Your program printed nothing.", None
    if len(lines) > 1:
        message = ("Your program should print a single line (the grade). "
                   "Remove your extra print() (counts, debugging...).")
        return f"{message}\n{printed}", None

    line = lines[0]
    if line == "Before Grade 1" or line == "Grade 16+":
        return None, line
    if line.startswith("Grade ") and line[6:].isdigit() and line[6] != "0":
        return None, line
    if line.startswith(USAGE):
        return (f"Your program printed the usage message, but the command "
                f"line is valid.\n{printed}"), None
    if line != line.strip():
        return (f"Nothing should be printed before or after the grade (not "
                f"even spaces).\n{printed}"), None
    if line.startswith("Grade ") and line.endswith(".0"):
        return (f"The grade must be an integer: round(index) gives an int, "
                f"but round(index, 0) gives a float.\n{printed}"), None
    if line.startswith("Grade -") or line == "Grade 0":
        return (f"When the grade is less than 1, your program should print "
                f"'Before Grade 1'.\n{printed}"), None
    if line.lower().startswith(("grade", "before grade")):
        return (f"The line must be written exactly as 'Grade X', "
                f"'Grade 16+' or 'Before Grade 1' (capital letters, one "
                f"space, no colon).\n{printed}"), None
    return (f"Your program should print 'Grade X', 'Grade 16+' or "
            f"'Before Grade 1'.\n{printed}"), None


def check_text(path, text):
    """Run one test on the file `path` containing `text`.

    Return (error message or None if the test passes,
            line printed by the program or None if not valid).
    """
    result = run_program([str(path)])
    if result is None:
        return "Your program did not stop (infinite loop?).", None
    stdout, stderr, _ = result
    if "Traceback" in stderr:
        return explain_crash(stderr), None
    message, given = check_line(stdout)
    if message is not None:
        return message, None

    expected = grade_line(text)
    if given != expected:
        return (f"Your program printed {given!r} instead of {expected!r}.\n"
                + explain_expected(text)), given
    return None, given


def diagnose(observations):
    """Explain the wrong results, using all the results of the program.

    observations: list of (text, line printed by the program).
    Return the explanations of the frequent mistakes (alone, or else two
    at a time) that give exactly the same results as the program.
    """
    def consistent(parameters):
        for text, given in observations:
            if grade_line(text, **parameters) != given:
                return False
        return True

    causes = []
    for parameters, explanation in MISTAKES:
        if consistent(parameters):
            causes.append(explanation)
    if causes:
        return causes
    for i, (parameters_1, explanation_1) in enumerate(MISTAKES):
        for parameters_2, explanation_2 in MISTAKES[i + 1:]:
            if parameters_1.keys() & parameters_2.keys():
                continue  # the two mistakes are about the same thing
            if consistent(parameters_1 | parameters_2):
                causes.append(explanation_1 + "\n    AND " + explanation_2)
    return causes


# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(errors="replace")
    use_colors = sys.stdout.isatty() and (
        os.name != "nt" or "WT_SESSION" in os.environ)
    green = "\033[32m" if use_colors else ""
    red = "\033[31m" if use_colors else ""
    reset = "\033[0m" if use_colors else ""

    if not (EXERCISE_DIR / SCRIPT).is_file():
        print(f"No {SCRIPT} found in {EXERCISE_DIR}")
        return 1

    nb_ok = 0
    nb_tests = len(CASES) + len(FILE_CASES) + len(USAGE_CASES)
    observations = []  # (text, line printed by the program)
    nb_wrong_results = 0

    shown = []  # explanations already printed

    def report(description, message, details):
        """Print the result of one test.

        An explanation already printed for a previous test is not
        repeated: only what the program printed is shown.
        """
        if message is None:
            print(f"{green}✔{reset} {description}")
            return 1
        print(f"{red}✗{reset} {description}")
        for detail in details:
            print(f"    {detail}")
        explanation, separator, printed = message.partition(
            "\nYour program printed:")
        if explanation in shown:
            message = "Same problem as above." + separator + printed
        else:
            shown.append(explanation)
        print("    " + message.replace("\n", "\n    ") + "\n")
        return 0

    with tempfile.TemporaryDirectory() as tmp_dir:
        tests = []
        for number, (description, text) in enumerate(CASES, start=1):
            path = Path(tmp_dir) / f"text_{number:02}.txt"
            path.write_text(text + "\n", encoding="utf-8")
            tests.append((description, path, text,
                          [f"Text in the file: {short(text)}"]))
        for description, file_name in FILE_CASES:
            path = EXERCISE_DIR / file_name
            if not path.is_file():
                print(f"{red}✗{reset} {description}")
                print(f"    {file_name} not found in {EXERCISE_DIR}\n")
                continue
            text = path.read_text(encoding="utf-8")
            tests.append((description, file_name, text,
                          [f"Command: python {SCRIPT} {file_name}"]))

        for description, path, text, details in tests:
            message, given = check_text(path, text)
            if given is not None:
                observations.append((text, given))
                if message is not None:
                    nb_wrong_results += 1
            nb_ok += report(description, message, details)

    for description, arguments in USAGE_CASES:
        message = check_usage(arguments)
        command = " ".join(["python", SCRIPT] + arguments)
        nb_ok += report(f"usage message: {description}", message,
                        [f"Command: {command}"])

    if nb_wrong_results > 0:
        causes = diagnose(observations)
        if not causes:
            print("To find your mistake, print the number of letters, "
                  "words and sentences computed by your program and "
                  "compare them with the expected ones (and remove these "
                  "print() afterwards).\n")
        else:
            title = "Probable cause" if len(causes) == 1 else "Possible causes"
            print(f"{title} of the wrong results, considering all the tests:")
            for cause in causes:
                print("  - " + cause)
            print()

    color = green if nb_ok == nb_tests else red
    print(f"Validated: {color}{nb_ok}/{nb_tests}{reset}")
    return 0 if nb_ok == nb_tests else 1


if __name__ == "__main__":
    sys.exit(main())
