"""
ECAT Exam Application — Dual Portal System
Submitted by : Nazish saghir 
Reg number : 2026(S)-CYS-21
Course  : CMPE-112L | CEA PROJECT
Professor : Hafiz Muhammad Mubashar
"""

import time
#CONSTANTS
CORRECT_MARKS   =  4
WRONG_MARKS     = -1
SKIP_MARKS      =  0
MIN_QUESTIONS   = 10
MAX_ATTEMPTS    =  3   

ADMIN_USERNAME  = "ecat_admin"
ADMIN_PASSWORD  = "ecat@2024"
STU_USERNAME    = "student"
STU_PASSWORD    = "student123"
#  QUESTIONS
questions = [
    {
        "id": 1,
        "subject": "mathematics",
        "question": "What is the value of log₂(8)?",
        "choices": {"A": "2", "B": "3", "C": "4", "D": "6"},
        "answer": "B"
    },
    {
        "id": 2,
        "subject": "mathematics",
        "question": "If f(x) = x² + 3x + 2, what is f(2)?",
        "choices": {"A": "8", "B": "10", "C": "12", "D": "14"},
        "answer": "C"
    },
    {
        "id": 3,
        "subject": "physics",
        "question": "What is the SI unit of electric current?",
        "choices": {"A": "Volt", "B": "Watt", "C": "Ampere", "D": "Ohm"},
        "answer": "C"
    },
    {
        "id": 4,
        "subject": "physics",
        "question": "Which law states F = ma?",
        "choices": {"A": "Newton's 1st Law", "B": "Newton's 2nd Law",
                    "C": "Newton's 3rd Law", "D": "Hooke's Law"},
        "answer": "B"
    },
    {
        "id": 5,
        "subject": "chemistry",
        "question": "What is the atomic number of Carbon?",
        "choices": {"A": "4", "B": "6", "C": "8", "D": "12"},
        "answer": "B"
    },
    {
        "id": 6,
        "subject": "chemistry",
        "question": "Which gas is produced when acid reacts with a metal?",
        "choices": {"A": "Oxygen", "B": "Carbon Dioxide", "C": "Hydrogen", "D": "Nitrogen"},
        "answer": "C"
    },
    {
        "id": 7,
        "subject": "mathematics",
        "question": "The sum of angles in a triangle is:",
        "choices": {"A": "90°", "B": "270°", "C": "180°", "D": "360°"},
        "answer": "C"
    },
    {
        "id": 8,
        "subject": "physics",
        "question": "The speed of light in vacuum is approximately:",
        "choices": {"A": "3×10⁶ m/s", "B": "3×10⁸ m/s",
                    "C": "3×10¹⁰ m/s", "D": "3×10⁴ m/s"},
        "answer": "B"
    },
    {
        "id": 9,
        "subject": "chemistry",
        "question": "Water is a compound of Hydrogen and:",
        "choices": {"A": "Nitrogen", "B": "Carbon", "C": "Oxygen", "D": "Sulfur"},
        "answer": "C"
    },
    {
        "id": 10,
        "subject": "mathematics",
        "question": "What is the square root of 144?",
        "choices": {"A": "11", "B": "12", "C": "13", "D": "14"},
        "answer": "B"
    },
    {
        "id": 11,
        "subject": "computer science",
        "question": "Which data type stores True or False in Python?",
        "choices": {"A": "int", "B": "str", "C": "float", "D": "bool"},
        "answer": "D"
    },
    {
        "id": 12,
        "subject": "computer science",
        "question": "What does CPU stand for?",
        "choices": {"A": "Central Process Unit",  "B": "Central Processing Unit",
                    "C": "Core Processing Unit",  "D": "Central Program Utility"},
        "answer": "B"
    },
]

all_results = []
#FUNCTIONS 
def print_line(char="─", width=60):
    print(char * width)


def print_header(title):
    
    print_line("═")
    print(f"  {title}")
    print_line("═")


def pause():
    time.sleep(0.8)


def get_grade(percentage):
    
    if percentage >= 80:
        return "EXCELLENT"
    elif percentage >= 65:
        return "GOOD"
    elif percentage >= 50:
        return "AVERAGE"
    else:
        return "BELOW AVERAGE"


def calculate_score(answers_dict):
   
    correct = 0
    wrong   = 0
    skipped = 0

    for idx, choice in answers_dict.items():
        if choice == "S":
            skipped += 1
        elif choice == questions[idx]["answer"]:
            correct += 1
        else:
            wrong += 1

    score = (correct * CORRECT_MARKS) + (wrong * WRONG_MARKS)
    return score, correct, wrong, skipped

#LOGIN FUNCTIONS
def admin_login():
    print_header("ADMIN LOGIN — ECAT Portal 1")
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        username = input("  Username : ").strip()
        password = input("  Password : ").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            print("\n  ✓ Login successful! Welcome, ECAT Admin.")
            pause()
            return True
        else:
            attempts += 1
            remaining = MAX_ATTEMPTS - attempts
            if remaining > 0:
                print(f"  ✗ Wrong credentials. {remaining} attempt(s) left.\n")
            else:
                print("  ✗ Account locked — too many failed attempts.")

    return False


def student_login():

    print_header("STUDENT LOGIN — ECAT Portal 2")
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        username = input("  Username  : ").strip()
        password  = input("  Password  : ").strip()

        if username == STU_USERNAME and password == STU_PASSWORD:
            print("  ✓ Login successful!")
            full_name   = input("  Full Name  : ").strip()
            roll_number = input("  Roll No.   : ").strip()
            pause()
            return True, full_name, roll_number
        else:
            attempts += 1
            remaining = MAX_ATTEMPTS - attempts
            if remaining > 0:
                print(f"  ✗ Wrong credentials. {remaining} attempt(s) left.\n")
            else:
                print("  ✗ Account locked — too many failed attempts.")

    return False, "", ""

#ADMIN PORTAL FUNCTIONS
def admin_view_all_questions():
    
    print_header("ALL QUESTIONS IN QUESTION BANK")

    if len(questions) == 0:
        print("  No questions found.")
        return

    for i, q in enumerate(questions):
        print(f"\n  Q{i + 1}. [{q['subject']}] {q['question']}")
        for key, val in q["choices"].items():
            marker = "✓" if key == q["answer"] else " "
            print(f"       {marker} {key}. {val}")

    print()


def admin_add_question():
    print_header("ADD NEW QUESTION")

    subject  = input("  Subject       : ").strip().lower()
    question = input("  Question text : ").strip()

    print("  Enter 4 choices:")
    choice_a = input("    A) ").strip()
    choice_b = input("    B) ").strip()
    choice_c = input("    C) ").strip()
    choice_d = input("    D) ").strip()

    while True:
        correct = input("  Correct answer (A/B/C/D): ").strip().upper()
        if correct in ["A", "B", "C", "D"]:
            break
        print("  ✗ Please enter A, B, C, or D only.")

    new_id = questions[-1]["id"] + 1 if questions else 1
    new_q  = {
        "id": new_id,
        "subject": subject,
        "question": question,
        "choices": {"A": choice_a, "B": choice_b, "C": choice_c, "D": choice_d},
        "answer": correct
    }
    questions.append(new_q)
    print(f"\n  ✓ Question added successfully! (Total: {len(questions)})")


def admin_delete_question():
    print_header("DELETE QUESTION")

    if len(questions) == 0:
        print("  No questions to delete.")
        return

    for i, q in enumerate(questions):
        print(f"  {i + 1}. {q['question'][:55]}...")

    try:
        num = int(input("\n  Enter question number to delete: "))
        if 1 <= num <= len(questions):
            removed = questions.pop(num - 1)
            print(f"\n  ✓ Deleted: \"{removed['question'][:50]}...\"")
        else:
            print("  ✗ Invalid number.")
    except ValueError:
        print("  ✗ Please enter a valid number.")


def admin_question_statistics():
    print_header("QUESTION BANK STATISTICS")

    subject_count = {}
    for q in questions:
        subject = q["subject"]
        subject_count[subject] = subject_count.get(subject, 0) + 1

    print(f"  Total Questions : {len(questions)}\n")
    print(f"  {'Subject':<25} {'Count':>5}")
    print_line("-", 35)
    for subject, count in subject_count.items():
        print(f"  {subject:<25} {count:>5}")
    print()


def admin_view_all_results():
    print_header("ALL STUDENT RESULTS")

    if len(all_results) == 0:
        print("  No student results yet.")
        return

    print(f"  {'#':<4} {'Name':<20} {'Roll':<12} {'Score':<8} {'%':<8} {'Grade':<14} {'Date/Time'}")
    print_line("-", 85)

    for i, result in enumerate(all_results):
        print(
            f"  {i + 1:<4} "
            f"{result['name']:<20} "
            f"{result['roll']:<12} "
            f"{result['score']:<8} "
            f"{result['percentage']:<8.1f} "
            f"{result['grade']:<14} "
            f"{result['datetime']}"
        )
    print()


def admin_view_detailed_result():

    print_header("VIEW DETAILED RESULT (PER STUDENT)")

    if len(all_results) == 0:
        print("  No results available.")
        return

    for i, result in enumerate(all_results):
        print(f"  {i + 1}. {result['name']} ({result['roll']}) — {result['datetime']}")

    try:
        num = int(input("\n  Enter result number: "))
        if not (1 <= num <= len(all_results)):
            print("  Invalid number.")
            return
    except ValueError:
        print("  Invalid input. Please enter a valid number.")
        return

    result = all_results[num - 1]
    print_header(f"Detailed Result — {result['name']} ({result['roll']})")

    answers_dict = result["answers"]

    for idx in range(len(questions)):
        q          = questions[idx]
        student_ans = answers_dict.get(idx, "S")
        correct_ans = q["answer"]

        if student_ans == "S":
            status = "SKIPPED"
        elif student_ans == correct_ans:
            status = "CORRECT  ✓"
        else:
            status = f"WRONG    ✗  (Correct: {correct_ans})"

        print(f"\n  Q{idx + 1}. {q['question']}")
        print(f"       Your Answer : {student_ans}   {status}")

    print(f"\n  Score      : {result['score']}")
    print(f"  Percentage : {result['percentage']:.1f}%")
    print(f"  Grade      : {result['grade']}\n")


def admin_class_statistics():
    print_header("CLASS RESULT STATISTICS")

    if len(all_results) == 0:
        print("  No results to analyse yet.")
        return

    scores = [r["score"] for r in all_results]
    highest = max(scores)
    lowest  = min(scores)
    average = sum(scores) / len(scores)

    passed = sum(1 for r in all_results if r["percentage"] >= 50)
    failed = len(all_results) - passed

    grade_count = {}
    for r in all_results:
        g = r["grade"]
        grade_count[g] = grade_count.get(g, 0) + 1

    print(f"  Total Attempts  : {len(all_results)}")
    print(f"  Highest Score   : {highest}")
    print(f"  Lowest Score    : {lowest}")
    print(f"  Average Score   : {average:.1f}")
    print(f"  Passed (≥50%)   : {passed}")
    print(f"  Failed (<50%)   : {failed}")
    print(f"\n  Grade Distribution:")
    for grade, count in grade_count.items():
        print(f"    {grade:<15} : {count}")
    print()


def admin_portal():
    if not admin_login():
        return

    while True:
        print_header("ADMIN PORTAL — Main Menu")
        print("  1. View All Questions")
        print("  2. Add New Question")
        print("  3. Delete a Question")
        print("  4. Question Bank Statistics")
        print("  5. View All Student Results")
        print("  6. View Detailed Result (Per Student)")
        print("  7. Class Result Statistics")
        print("  8. Logout")
        print_line()

        choice = input("  Enter option (1-8): ").strip()

        if choice == "1":
            admin_view_all_questions()
        elif choice == "2":
            admin_add_question()
        elif choice == "3":
            admin_delete_question()
        elif choice == "4":
            admin_question_statistics()
        elif choice == "5":
            admin_view_all_results()
        elif choice == "6":
            admin_view_detailed_result()
        elif choice == "7":
            admin_class_statistics()
        elif choice == "8":
            print("\n  Logged out. Goodbye, Admin!\n")
            break
        else:
            print("  ✗ Invalid option. Please choose 1-8.\n")

        input("  Press Enter to continue...")

#STUDENT PORTAL FUNCTIONS
def show_exam_rules():
    print_header("EXAM RULES & INSTRUCTIONS")
    print("  • The exam has", len(questions), "MCQ questions.")
    print("  • Each question has 4 choices: A, B, C, D.")
    print()
    print("  Marking Scheme:")
    print(f"    Correct Answer  : +{CORRECT_MARKS} marks")
    print(f"    Wrong Answer    : {WRONG_MARKS} mark")
    print(f"    Skipped         :  {SKIP_MARKS} marks")
    print()
    print("  During the exam:")
    print("    • Type A / B / C / D  to answer.")
    print("    • Type S              to skip a question.")
    print("    • Type SUBMIT         to end the exam early.")
    print()
    print("  The exam auto-submits when all questions are answered.")
    print()


def conduct_exam(student_name, roll_number):

    answers = {}  

    print_header(f"EXAM STARTED — {student_name} ({roll_number})")
    print(f"  Total Questions : {len(questions)}")
    print("  Type SUBMIT at any time to end early.\n")

    for idx in range(len(questions)):
        q = questions[idx]
        print(f"\n  Question {idx + 1} of {len(questions)}  [{q['subject']}]")
        print(f"  {q['question']}")
        for key, val in q["choices"].items():
            print(f"    {key}. {val}")

       
        while True:
            raw = input("\n  Your answer (A/B/C/D  |  S=Skip  |  SUBMIT): ").strip().upper()

            if raw == "SUBMIT":
                # Mark remaining questions as skipped
                for remaining in range(idx, len(questions)):
                    if remaining not in answers:
                        answers[remaining] = "S"
                print("\n  Exam submitted early.")
                return answers

            elif raw in ["A", "B", "C", "D"]:
                answers[idx] = raw
                break

            elif raw == "S":
                answers[idx] = "S"
                print(" Question skipped.")
                break

            else:
                print("  Invalid input. Please type A, B, C, D, S, or SUBMIT.")

    print("\n  All questions answered — exam auto-submitted.")
    return answers


def show_student_result(student_name, roll_number, answers_dict):

    max_score  = len(questions) * CORRECT_MARKS
    score, correct, wrong, skipped = calculate_score(answers_dict)
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    grade      = get_grade(percentage)
    exam_time  = time.strftime("%Y-%m-%d %H:%M:%S")

   
    result_record = {
        "name"       : student_name,
        "roll"       : roll_number,
        "score"      : score,
        "max_score"  : max_score,
        "correct"    : correct,
        "wrong"      : wrong,
        "skipped"    : skipped,
        "percentage" : percentage,
        "grade"      : grade,
        "datetime"   : exam_time,
        "answers"    : answers_dict
    }
    all_results.append(result_record)
#RESULT DISPLAY
    print_header("YOUR EXAM RESULT")
    print(f"  Name       : {student_name}")
    print(f"  Roll No.   : {roll_number}")
    print(f"  Date/Time  : {exam_time}")
    print_line("-")
    print(f"  Correct    : {correct}  (+{correct * CORRECT_MARKS} marks)")
    print(f"  Wrong      : {wrong}  ({wrong * WRONG_MARKS} marks)")
    print(f"  Skipped    : {skipped}  (0 marks)")
    print_line("-")
    print(f"  Score      : {score} / {max_score}")
    print(f"  Percentage : {percentage:.1f}%")
    print(f"  Grade      : {grade}")
    print_line("═")

    #ANSWER REVIEW
    print("\n  ANSWER REVIEW:")
    print_line("-")
    for idx in range(len(questions)):
        q           = questions[idx]
        student_ans = answers_dict.get(idx, "S")
        correct_ans = q["answer"]

        if student_ans == "S":
            status = "SKIPPED"
        elif student_ans == correct_ans:
            status = "CORRECT ✓"
        else:
            status = f"WRONG ✗  (Correct: {correct_ans})"

        print(f"  Q{idx + 1:>2}. {q['question'][:45]:<45}  You: {student_ans}  {status}")

    print()


def student_portal():
    logged_in, name, roll = student_login()
    if not logged_in:
        return

    while True:
        print_header(f"STUDENT PORTAL — {name} ({roll})")
        print("  1. Start Exam")
        print("  2. View Exam Rules")
        print("  3. Logout")
        print_line()

        choice = input("  Enter option (1-3): ").strip()

        if choice == "1":
            answers = conduct_exam(name, roll)
            show_student_result(name, roll, answers)
        elif choice == "2":
            show_exam_rules()
        elif choice == "3":
            print(f"\n  Logged out. Good luck, {name}!\n")
            break
        else:
            print("  ✗ Invalid option. Please choose 1-3.\n")

        input("  Press Enter to continue...")


#INTERFACE
def main():
    while True:
        print_header("ECAT EXAM APPLICATION — Dual Portal System")
        print("  University of Engineering & Technology, Lahore")
        print("  Course : CMPE-112L  |  Lab #1\n")
        print("  1. Admin Portal  (ECAT Team)")
        print("  2. Student Portal")
        print("  3. Exit")
        print_line()

        choice = input("  Select portal (1/2/3): ").strip()

        if choice == "1":
            admin_portal()
        elif choice == "2":
            student_portal()
        elif choice == "3":
            print("\n  Thank you for using the ECAT Exam App. Goodbye!\n")
            break
        else:
            print("  ✗ Invalid choice. Please enter 1, 2, or 3.\n")

#RUN APP
if __name__ == "__main__":
    main()
