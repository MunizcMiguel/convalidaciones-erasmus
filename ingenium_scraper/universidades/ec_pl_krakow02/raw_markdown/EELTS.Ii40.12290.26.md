---
{
 "course_code": "EELTS.Ii40.12290.26",
 "course_name": "Texas Instruments DSP in automotive – advanced",
 "institution_slug": "ec_pl_krakow02",
 "source_url": "https://sylabusy.agh.edu.pl/en/document/1526aeb0-f87d-426c-bc93-b90396ded007.html",
 "source_language": "pl",
 "ects_catalog": 4.0,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-20T08:22:54",
 "content_sha256": "475d4a7d7d6bf6941b8d9d50cbb281bdb94bc58af3ebd77c6f83aba234ca1e61"
}
---

# Texas Instruments DSP in automotive – advanced

## Basic information

- **Field of study**: Electrical Engineering
- **Major**: -
- **Organisational unit**: Faculty of Electrical Engineering, Automatics, Computer Science and Biomedical Engineering
- **Study level**: First-cycle (engineer) programme
- **Form of study**: Full-time studies
- **Profile**: General academic

- **Didactic cycle**: 2026/2027
- **Course code**: EELTS.Ii40.12290.26
- **Lecture languages**: English
- **Mandatoriness**: Elective
- **Block**: Core Modules
- **Course related to scientific research**: No

- **Period**: Semester 7
- **Method of verification of the learning outcomes**: Completing the classes; Activities and hours; Discussion seminars: 28 Laboratory classes: 20
- **Number of ECTS credits**: 4

## Goals

- **C1**: • Students will learn how to program and configure built-in Texas Instruments C2000 series floating-point microcontroller peripherals (TMS320F28379D - dual-core version) using Matlab / SIMULINK environment and the option of automatic code generation in C. • Students learn the rules of programming in the dedicated programming environment CodeComposerStudio (CCS) and the method of code implementation in Matlab / SIMULINK with an extension to C2000 chips. • Students will learn how to prepare and properly configure a project and learn debugging methods.
- **C2**: • Students will gain practical knowledge and skills in the use of interrupt systems available in the TMS320F28379D microcontroller and the proper configuration of built-in peripherals based on the Texas Instruments evaluation kit extended with external signal interface systems, i.e .: i) GPIO digital inputs / outputs, ii) counters, iii) ePWM generators, iv) eQEP modules dedicated to the encoder, v) eCAP modules allowing for measuring the duration of external events, (vi) analog / digital converters (ADC) and (vii) digital / analog converters (DAC).
- **C3**: • Students will gain practical knowledge and skills in the operation of propulsion systems and power electronics systems dedicated to electric vehicles and the infrastructure necessary for their charging in the Matlab / SIMULINK environment and transfer of the developed measurement, control or protection structure to a floating-point microcontroller using the option of automatic code generation in C.

## Course's learning outcomes

| Code | Outcomes in terms of | Learning outcomes prescribed to a field of study | Methods of verification |
|---|---|---|---|
| Knowledge – Student knows and understands: |  |  |  |
| W1 | Structure of a TI C2000 series floating-point microcontroller with two cores | ELT1A_W05, ELT1A_W07 | Presentation |
| W2 | Methods of project preparation and control as well as the basics of programming in Matlab / SIMULINK environment, including automatic code generation in C for C2000 microcontrollers | ELT1A_W05, ELT1A_W07 | Presentation |
| W3 | The challenges of the automotive industry, in particular electric vehicles and the infrastructure necessary to charge them. | ELT1A_W10 | Presentation |
| W4 | Motors used in electric cars - machines with permanent magnets | ELT1A_W08 | Presentation |
| W5 | Power electronics used in electric vehicles | ELT1A_W06 | Presentation |
| Skills – Student can: |  |  |  |
| U1 | plan and conduct a project; interpret the obtained results and draw conclusions using analytical, simulation and experimental methods | ELT1A_U03 | Work done within the framework of a practical placement |
| U2 | work with technical documentation prepared by the manufacturer of the microcontroller | ELT1A_U02 | Work done within the framework of a practical placement |
| U3 | wykorzystywać posiadaną wiedzę, formułować i rozwiązywać nietypowe problemy | ELT1A_U01 | Work done within the framework of a practical placement |
| Social competences – Student is ready to: |  |  |  |
| K1 | practical implementation and development of control, control and security algorithms dedicated to electric drives and power electronic systems used in vehicles | ELT1A_K03 | Work done within the framework of a practical placement, Presentation |
| K2 | evaluation of knowledge and received content, supplementing and improving acquired knowledge and skills, setting priorities for the implementation of assigned tasks | ELT1A_K01 | Work done within the framework of a practical placement, Presentation |

## Program content ensuring the achievement of the learning outcomes prescribed to the module

Graduates can use the acquired competences when starting work in various sectors of the economy wherever there is a need to use a microcontroller for i) control and control of drive systems with electric motors, ii) control and control of power electronic converters and iii) measurement of electrical quantities.

## Student workload

- **Activity form**: Average amount of hours* needed to complete each activity form
- **Discussion seminars**: 28
- **Laboratory classes**: 20
- **Preparation for classes**: 12
- **Preparation of project, presentation, essay, report**: 30
- **Realization of independently performed tasks**: 10
- **Student workload**: Hours 100
- **Workload involving teacher**: Hours 48

* hour means 45 minutes

## Program content

| No. | Program content | Course's learning outcomes | Activities |
|---|---|---|---|
| 1. | Introduction to issues related to electric vehicles and their charging infrastructure - defining the main challenges for the development of e-mobility. Overview of drive systems with electric motors used in electric cars - development of a model of the drive system together with control, control and protection algorithms in the Matlab / SIMULINK simulation environment. Overview of the topology of power electronic systems with the control and control structure used in electric vehicles and chargers - developing a model of the converter system in the Matlab / SIMULINK environment that allows for the correct power supply of the electric motor and charging the car battery from an external charger (wired or wireless). Indication and discussion of external peripheral modules available in TI microcontrollers from the C2000 family, enabling the effective implementation of the developed control, control and protection algorithms into a digital system. Discussion of the advantages and basic differences resulting from the programming of microprocessor systems with a floating decimal point in relation to digital systems with fixed-point architecture - explaining the methods of data type conversion in the Matlab / SIMULINK environment and effective program code creation. Discussion in details of the signal microcontroller architecture with an explanation of how to configure individual peripheral modules and each of the two cores (using the libraries available in the Matlab / SIMULINK environment for this purpose) - presentation of the concept of project preparation with the option of automatic code generation in C from the Matlab simulation environment / SIMULINK. | W1, W2, W3, W4, W5, K1, K2 | Discussion seminars |
| 2. | Development of a model of a drive system with an improved engine and a standard of control, control and security in Matlab / SIMULINK licenses - learning effective model preparation, data conversion, defining permanent global tests in the program. Basic summary Development of bipolar and unipolar control for the BLDC motor Preparation of an algorithm to close the regulating loop for the BLDC motor - motor control Analyzing the operation of the engine with bipolar control and unipolarity - a change in the automation algorithm and speed regulation Preparation of the DC-DC system for voltage reduction as a power supply for a lamp with a light-emitting diode (LED) Preparation of an algorithm to check the voltage and the output voltage. Test the DC-DC circuit and the PI regulator settings for controlling the output voltage | U1, U2, U3, K1, K2 | Laboratory classes |

## Extended information/Additional elements

### Teaching methods and techniques :

Group work, Design thinking, Project Based Learning

| Activities | Methods of verification | Credit conditions |
|---|---|---|
| Discussion seminars | Presentation | Presentation |
| Lab. classes | Work done within the framework of a practical placement | Work as part of the project |

### Conditions and the manner of completing each form of classes, including the rules of making retakes, as well as the conditions for admission to the exam

The final grade will be calculated according to the AGH University of Science and Technology Study Regulations

### Method of determining the final grade

The final grade will be calculated according to the AGH University of Science and Technology Study Regulations

### Manner and mode of making up for the backlog caused by a student justified absence from classes

Determined by the lecturer teacher

## Prerequisites and additional requirements

The program of the subject implements the learning outcomes in the field of knowledge, skills and competencies in the field of Electronics, Electrical Engineering, and Automation and Robotics, in particular: competence to use and practical use of the software.

### Rules of participation in given classes, indicating whether student presence at the lecture is obligatory

Presence is compulsory

## Literature

Obligatory

- LAUNCHXL-F28379D C2000 Delfino MCU F28379D LaunchPad™ development kit - https://www.ti.com/tool/LAUNCHXL-F28379D

Optional

- C2000™ real-time control MCUs Optimized for processing, sensing, and actuation to improve closed loop performance - https://www.ti.com/microcontrollers/c2000-real-time-control-mcus/overview.html?keyMatch=C2000&tisearch=Search-EN-everything
