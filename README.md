# symptom_checker
symptom checker: a Tkinter app that scores conditions from symptoms, age, and duration and rates risk.
# Symptom Checker Pro

A rule-based medical triage assistant built with Python and Tkinter. It analyzes a user's symptoms, severity, age, and illness duration to suggest possible conditions and rate overall risk.

> **Disclaimer:** This is an educational project and is **not** a medical diagnosis tool. Always consult a qualified healthcare professional. In an emergency, call your local emergency number.

## Features

- **Weighted symptom scoring:** each condition has symptoms with different weights, so a telling symptom (like loss of smell) counts more than a common one (like cough).
- **Severity adjustment:** every symptom can be marked Mild, Moderate, or Severe, which changes how much it counts.
- **Risk rating:** a color-coded LOW, MODERATE, or HIGH rating based on red-flag symptoms, severity, match strength, age, and duration.
- **Visual results:** the top matching conditions are shown as percentage bars.
- **Care advice:** basic self-care guidance for the top match, plus the reasons behind the risk rating.
- **History tracking:** every check is saved to `history.csv` and shown in a History tab.
- **Dark theme:** set `DARK_MODE = False` in the code for the light theme.

## How It Works

1. The user enters age, days sick, and selects symptoms with a severity for each.
2. The input is validated (age 0-120, at least one symptom).
3. For each condition: `match % = sum(symptom weight x severity multiplier) / total weight x 100` (capped at 100).
4. Risk points are added for: a red-flag symptom (+3), three or more severe symptoms (+1), a top match of 60% or higher (+1), age under 5 or over 65 (+1), and illness lasting over 7 days (+1).
5. Points of 3 or more give HIGH, 2 gives MODERATE, and otherwise LOW.
6. Results are displayed and saved to history.

## Conditions Covered

Common Cold, Influenza (Flu), COVID-19, Allergies, Migraine, and Food Poisoning. More can be added by editing the `CONDITIONS` dictionary.

## Requirements

- Python 3.8 or newer
- Tkinter (included with most Python installations)

No external libraries are needed.

## Run the Project

```
python symptom_checker_pro.py
```

On some Linux systems you may need to install Tkinter first: `sudo apt install python3-tk`

## Project Structure

```
symptom_checker_pro.py   Main application (logic and GUI)
history.csv              Created automatically after the first check
```

## Limitations

- Uses simple rules and weights, not machine learning or clinical data.
- Covers only a small set of conditions and symptoms.
- Cannot replace professional medical advice.

## Future Improvements

- Add more conditions and symptoms
- Export a report as PDF
- Train a machine learning model on a real medical dataset
- Add multi-language support

## License

This project is for educational purposes.
