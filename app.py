import os
import re
import uuid
import base64
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify


# Configuration (updated with your provided values)
ACCESS_TOKEN = os.getenv('WA_ACCESS_TOKEN', "EACHWo8LZCYRwBP5s6kfto6U1yTV6dWVUHiOKlZCEOx0rkHZBPPBbPEf8Esypwq4nR5ZCxtodgMkVA0LyMdqHuJLCAFisTBY76ASiZAT2WZBRrDQGz2bAKlGv2QnGUobEsZBDB4NWOkDUSh5nwp0PpmXsFZCQZAM35wU7Xst3t5r0wmZCri7p5JdCB5KkVzZAyzzKcDUZCYDJD4aylOyYkAQNAGLubTsZCyDJuSQlQm3SGgCvIeA4G6lnXCq5WXUjUrcqL1gZDZD")  # Replace with your token
PHONE_NUMBER_ID = os.getenv('WA_PHONE_ID', "579796315228068")  # Replace with your phone ID
API_VER = "v18.0"  # Stable version
WA_URL = f"https://graph.facebook.com/{API_VER}/{PHONE_NUMBER_ID}/messages"
VERIFY_TOKEN = os.getenv('WA_VERIFY_TOKEN', "MY_UNIQUE_VERIFY_TOKEN_123")

# *** ROUTE EVERYTHING TO THE NEW APPS SCRIPT ***
APPSCRIPT_URL    = os.getenv('APPSCRIPT_URL', "https://script.google.com/macros/s/AKfycbz9DPnJ4lNZhFBWuExDiJN_H3y-XTZ50H-DCXSTOiP7d3HA0TIYbDrJ-_ZS-0na0viI/exec")

OPENROUTER_KEY   = os.getenv('OPENROUTER_KEY', "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")
OPENROUTER_MODEL = "qwen/qwen3-30b-a3b:free"
OPENROUTER_API   = "https://openrouter.ai/api/v1/chat/completions"

# NEW: Admin/Drive/Calendar settings
ADMIN_EMAIL     = os.getenv("ADMIN_EMAIL", "solutions@nexabloom.io")
# From your Drive folder link: https://drive.google.com/drive/folders/1qobSLoixuJILlkSP-nIo4qOHzVOLMpWv
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "1qobSLoixuJILlkSP-nIo4qOHzVOLMpWv")
CALENDLY_URL    = os.getenv("CALENDLY_URL", "")     # optional
CAL_DEFAULT_TZ  = os.getenv("CAL_TZ", "Europe/London")
MAX_MEDIA_BYTES = int(os.getenv("MAX_MEDIA_BYTES", str(12*1024*1024)))  # 12MB
GRAPH_BASE      = f"https://graph.facebook.com/{API_VER}"

# SHEET target (from your link)
SHEET_ID        = os.getenv("SHEET_ID", "105mrH6iAIPzUJ035iHymxIjS7FaEnPcPeb3hIdgBr-s")
SHEET_TAB       = os.getenv("SHEET_TAB", "Cases")  # change if your tab name differs

# WhatsApp interactive limits to prevent silent UI drops
WALIM = {"list_title": 24, "list_desc": 72, "button": 20, "header": 60, "body": 1024, "rows": 10}

# SERVICES with full subservices, questions, checklists, next_steps and expanded faqs
SERVICES = {
    "Family Immigration": {
        "subservices": {
            "Spouse/Partner Visa": {
                "questions": [
                    "Is your partner a British citizen or settled in the UK?",
                    "Are you married or in a civil partnership?",
                    "Have you lived together for 2+ years?",
                    "Do you meet the financial requirement (£18,600/year)?",
                    "Do you have suitable accommodation in the UK?",
                    "Have you passed an English language test (A1 level)?",
                    "Do you have dependent children applying?",
                    "Have you had previous UK visa refusals?",
                    "Is your relationship genuine and subsisting?",
                    "Do you intend to live permanently in the UK?"
                ],
                "checklist": [
                    "Valid passport",
                    "Marriage/civil partnership certificate",
                    "Proof of relationship (photos, chats, joint bills)",
                    "Financial documents (payslips, bank statements)",
                    "Accommodation proof (tenancy agreement)",
                    "English test certificate",
                    "TB test certificate (if applicable)",
                    "Children's birth certificates (if applicable)",
                    "Previous refusal letters (if applicable)",
                    "Sponsor's citizenship/ILR proof"
                ],
                "next_steps": "Prepare and submit your application. A lawyer will contact you. Check GOV.UK for updates.",
                "faqs": [
                    {"q": "Financial requirement?", "a": "The minimum financial requirement is £18,600 per year from employment, self-employment, or permitted benefits.\nSavings can be used if they exceed £62,500 for cash savings alone.\nFor additional children, add £3,800 for the first and £2,400 for each subsequent child."},
                    {"q": "Processing time?", "a": "Standard processing takes 2-3 months for applications from outside the UK.\nPriority service can reduce it to 6 weeks, but availability varies by country.\nIn the UK, extensions typically take 8 weeks."},
                    {"q": "Can I work?", "a": "Yes, you are allowed to work in the UK on a Spouse/Partner Visa without restrictions.\nYou can also study, but you must meet course requirements separately.\nSelf-employment is permitted, but public funds access is restricted."},
                    {"q": "English test needed?", "a": "An A1 level English test is required unless you're from a majority English-speaking country or have a degree taught in English.\nExemptions apply for those over 65 or with disabilities.\nApproved tests include IELTS, Trinity, or PTE; check GOV.UK for providers."},
                    {"q": "Documents required?", "a": "Core documents include passport, marriage certificate, proof of relationship like joint bills or photos, and financial evidence such as payslips.\nAccommodation details, English test results, and TB certificate if applicable.\nAll non-English documents must be translated and certified."},
                    {"q": "Partner not British?", "a": "Your partner must be a British citizen, have indefinite leave to remain, or refugee/humanitarian protection status.\nEU citizens with settled status also qualify under the scheme.\nTemporary visa holders like students or workers do not qualify as sponsors."},
                    {"q": "Visa duration?", "a": "Initial grant is 2.5 years (30 months) from outside the UK or 2 years and 9 months from inside.\nExtensions are possible for another 2.5 years.\nAfter 5 years, you can apply for indefinite leave to remain (settlement)."},
                    {"q": "Bring children?", "a": "Yes, dependent children under 18 can apply, but financial threshold increases by £3,800 for the first and £2,400 each additional.\nChildren must not be leading independent lives.\nSeparate applications for children over 18 are rare and require exceptional circumstances."},
                    {"q": "Fiancé vs Spouse?", "a": "Fiancé visa is for those intending to marry in the UK within 6 months, then switch to spouse visa.\nSpouse visa is for already married couples or civil partners.\nFiancé visa doesn't allow work initially, while spouse does."},
                    {"q": "Prove genuine relationship?", "a": "Provide evidence like joint finances, correspondence, photos from different times, and affidavits from friends/family.\nCohabitation proof for 2 years if unmarried.\nHome Office assesses subsisting relationship and intention to live together permanently."}
                ]
            },
            "Parent Visa": {
                "questions": [
                    "Is your child under 18 and British/settled?",
                    "Do you have sole responsibility?",
                    "Financial requirement met (£18,600+)?",
                    "Suitable accommodation?",
                    "English test (A1)?",
                    "Previous refusals?",
                    "Intend permanent stay?",
                    "Child's consent if shared custody?",
                    "Genuine parental relationship?",
                    "No other caregivers?"
                ],
                "checklist": [
                    "Passport",
                    "Child's birth certificate",
                    "Proof of sole responsibility",
                    "Financial docs",
                    "Accommodation proof",
                    "English cert",
                    "TB test",
                    "Custody docs",
                    "Relationship proof",
                    "Sponsor's details"
                ],
                "next_steps": "Submit application with evidence of relationship.",
                "faqs": [
                    {"q": "Age limit for child?", "a": "The child must be under 18 at the time of application.\nIf over 18, they may not qualify unless exceptional circumstances apply.\nApplications for children turning 18 soon should be submitted promptly."},
                    {"q": "Financial req?", "a": "Sponsor must meet £18,600 annual income, plus £3,800 for the first child and £2,400 for each additional.\nSavings or permitted benefits can count towards this.\nEvidence like payslips or tax returns is required for 6-12 months."},
                    {"q": "Can I work?", "a": "Yes, Parent Visa holders can work in the UK without restrictions.\nYou can also study, but access to public funds is limited.\nSelf-employment is allowed as long as financial requirements are met."},
                    {"q": "English needed?", "a": "A1 level English test is required unless exempt (e.g., over 65 or disability).\nApproved tests from designated providers only.\nNationals from majority English-speaking countries are exempt."},
                    {"q": "Documents?", "a": "Include child's birth certificate, proof of sole responsibility like court orders, financial documents, and accommodation evidence.\nEnglish test and TB certificate if applicable.\nAll documents must be original or certified copies with translations."},
                    {"q": "Both parents apply?", "a": "Both can apply if they meet the requirements individually.\nIf one parent is applying, evidence of sole responsibility or serious circumstances is needed.\nJoint applications require higher financial thresholds if children are included."},
                    {"q": "Duration?", "a": "Initial grant is 2.5 years, extendable.\nAfter 5 years, eligible for indefinite leave to remain.\nContinuous residence and Life in UK test required for settlement."},
                    {"q": "Bring other children?", "a": "Yes, if they are dependents under 18 and meet financial increases.\nEach additional child raises the threshold.\nIndependent children over 18 generally do not qualify."},
                    {"q": "Sole responsibility proof?", "a": "Provide court orders, affidavits from the other parent, or evidence of full care.\nSchool letters or medical records showing primary caregiving.\nHome Office assesses if the parent has continuing control and direction of child's upbringing."},
                    {"q": "TB test?", "a": "Required for applicants from certain countries listed on GOV.UK.\nTest from approved clinic only, valid for 6 months.\nChildren under 11 may be exempt in some cases."}
                ]
            },
            "Child Visa": {
                "questions": [
                    "Parent British/settled?",
                    "Under 18?",
                    "Financial met?",
                    "Accommodation?",
                    "English if school age?",
                    "Refusals?",
                    "Genuine relationship?",
                    "Sole responsibility?",
                    "Both parents applying?",
                    "Intend settle?"
                ],
                "checklist": [
                    "Passport",
                    "Birth cert",
                    "Parental consent",
                    "Financials",
                    "Accommodation",
                    "English if needed",
                    "TB test",
                    "School letter",
                    "Relationship proof",
                    "Sponsor docs"
                ],
                "next_steps": "Apply with parent sponsor.",
                "faqs": [
                    {"q": "Age limit?", "a": "Child must be under 18 at application time.\nOver 18s may apply in exceptional cases if dependent.\nApplications close to 18th birthday should be prioritized."},
                    {"q": "Financial?", "a": "£18,600 base plus £3,800 for first child, £2,400 each additional.\nSponsor provides evidence like employment or savings.\nNo recourse to public funds."},
                    {"q": "Work/study?", "a": "Children can study full-time; work is limited to part-time for 16+.\nNo full-time employment allowed.\nEducation plans may require school enrollment proof."},
                    {"q": "English?", "a": "Not required for children under school age.\nSchool-age children may need basic English, but usually exempt.\nSponsor handles language requirements if applicable."},
                    {"q": "Documents?", "a": "Birth certificate, parental consent if not both applying, financial proof, accommodation details.\nPassport and TB test if needed.\nRelationship evidence like photos or DNA if doubted."},
                    {"q": "Independent child?", "a": "Rare; must prove not leading independent life.\nUsually for under 18s with settled parent.\nOver 18s need compelling reasons."},
                    {"q": "Duration?", "a": "Matches the parent's visa duration.\nRenewable until child is 18 or independent.\nPath to settlement after 5 years if eligible."},
                    {"q": "Multiple children?", "a": "Yes, each on separate application but financials cumulative.\nAll must meet dependency criteria.\nGroup applications simplify process."},
                    {"q": "Proof relationship?", "a": "Birth certificate primary; DNA test if requested by Home Office.\nAdditional evidence like family photos or school records.\nGenuine parent-child relationship assessed."},
                    {"q": "TB?", "a": "Required for children from listed countries.\nClinic-approved test valid 6 months.\nUnder 11s may have chest x-ray exemption in some cases."}
                ]
            },
            "Adult Dependent Relative": {
                "questions": [
                    "Sponsor settled/British?",
                    "Require long-term care?",
                    "Care not available/affordable in home country?",
                    "Sponsor meet financial (£18,600)?",
                    "Accommodation without public funds?",
                    "English A1?",
                    "TB test?",
                    "Refusals?",
                    "Genuine dependency?",
                    "No other relatives?"
                ],
                "checklist": [
                    "Passport",
                    "Medical reports",
                    "Proof care unavailable home",
                    "Financials",
                    "Accommodation",
                    "English cert",
                    "TB cert",
                    "Relationship proof",
                    "Sponsor undertaking",
                    "Previous visas"
                ],
                "next_steps": "Evidence strict; consult lawyer.",
                "faqs": [
                    {"q": "Who qualifies?", "a": "Typically parents or grandparents needing long-term personal care due to age, illness, or disability.\nSiblings or other relatives rarely qualify.\nSponsor must be British/settled and able to maintain without public funds."},
                    {"q": "Financial?", "a": "Sponsor must meet £18,600 income threshold.\nNo additional for dependents as it's settlement route.\nEvidence of ability to support long-term without recourse to public funds."},
                    {"q": "Work?", "a": "No work allowed on this visa.\nFocus is on dependency and care.\nSwitching to work visas later possible but difficult."},
                    {"q": "English?", "a": "A1 level required unless exempt (age/disability).\nTest from approved provider.\nExemptions need medical evidence."},
                    {"q": "Documents?", "a": "Medical reports showing care needs, proof no adequate care in home country (cost/availability), financials from sponsor.\nRelationship proof like birth certificates.\nAccommodation and maintenance undertaking."},
                    {"q": "Appeal rate?", "a": "High refusal rate due to strict evidence requirements.\nAppeals possible on human rights grounds.\nLegal advice strongly recommended pre-application."},
                    {"q": "Duration?", "a": "Indefinite leave to enter/remain if approved.\nNo extensions needed.\nPath to citizenship after settlement."},
                    {"q": "Siblings?", "a": "Siblings do not qualify under standard rules.\nOnly parents/grandparents typically.\nExceptional compassionate cases rare."},
                    {"q": "Proof dependency?", "a": "Detailed medical evidence from professionals.\nProof no adequate care in home country (cost/availability).\nSponsor must show ability to provide care."},
                    {"q": "TB?", "a": "Required for applicants from certain countries.\nApproved clinic test valid 6 months.\nResults submitted with application."}
                ]
            }
        }
    },
    "Work Immigration": {
        "subservices": {
            "Skilled Worker Visa": {
                "questions": [
                    "Job offer from approved sponsor?",
                    "Job at RQF6+ (2025 rule)?",
                    "Salary £41,700+ or going rate?",
                    "English test passed?",
                    "Relevant PhD for points?",
                    "Job on Immigration Salary List?",
                    "Previous refusals?",
                    "Criminal record check needed?",
                    "Healthcare/education role?",
                    "Meet 70 points total?"
                ],
                "checklist": [
                    "Certificate of Sponsorship (CoS)",
                    "English proficiency proof (e.g., IELTS)",
                    "Valid passport",
                    "Job details (title, salary, code)",
                    "Sponsor licence details",
                    "Criminal record certificate (if required)",
                    "Certified translations",
                    "TB test certificate",
                    "PhD proof if applicable",
                    "Financial proof if needed"
                ],
                "next_steps": "Sponsor issues CoS. Apply online. Note 2025 salary £41,700.",
                "faqs": [
                    {"q": "Min salary 2025?", "a": "£41,700 or the going rate for the job, whichever higher.\nDiscounts for new entrants or shortage occupations.\nSalary must be from guaranteed basic pay, no overtime."},
                    {"q": "Skill level?", "a": "Job must be at RQF level 6 or above (graduate level).\nCheck SOC code on GOV.UK.\nLower levels not eligible from 2025."},
                    {"q": "English req?", "a": "B1 level in speaking, listening, reading, writing.\nTest from approved provider or degree taught in English.\nNationals from English-majority countries exempt."},
                    {"q": "Points system?", "a": "70 points required: 50 mandatory (offer, skill, English), 20 tradeable (salary, PhD, shortage).\nCalculate on GOV.UK points calculator.\nMandatory points cannot be traded."},
                    {"q": "Documents?", "a": "CoS reference, English test, passport, job description.\nCriminal record for certain sectors.\nTB test and financial proof if needed."},
                    {"q": "Duration?", "a": "Up to 5 years, extendable.\nIndefinite leave after 5 years if eligible.\nCooling-off period for repeat applications."},
                    {"q": "Dependents?", "a": "Yes, partner and children under 18.\nHigher financial threshold for family.\nDependents can work/study with restrictions."},
                    {"q": "Switch jobs?", "a": "New CoS from new sponsor required.\nUpdate visa before starting new job.\nSame sector/salary rules apply."},
                    {"q": "ILR?", "a": "After 5 years continuous residence.\nLife in UK test and B1 English.\nAbsences under 180 days per year."},
                    {"q": "TB test?", "a": "Required for applicants from listed countries.\nApproved clinic, valid 6 months.\nExempt for short stays or certain diplomats."}
                ]
            },
            "Health and Care Worker Visa": {
                "questions": [
                    "Job in health/care?",
                    "Sponsor licensed?",
                    "Salary £29,000+ (2025)?",
                    "English B1?",
                    "No new care workers overseas (2025)?",
                    "Refusals?",
                    "Criminal check?",
                    "Regulated profession?",
                    "Meet points?",
                    "Dependents?"
                ],
                "checklist": [
                    "CoS",
                    "English proof",
                    "Passport",
                    "Job details",
                    "Sponsor info",
                    "Criminal cert",
                    "Professional registration",
                    "TB test",
                    "Financials",
                    "Dependents docs"
                ],
                "next_steps": "Note 2025 restrictions on care workers.",
                "faqs": [
                    {"q": "Eligible jobs?", "a": "NHS roles, social care (limited to regulated from 2025).\nPrivate health also qualifies if sponsored.\nCheck SOC codes for health/care occupations."},
                    {"q": "Salary?", "a": "Minimum £29,000 or going rate, lower threshold than standard skilled worker.\nDiscounts for new entrants.\nMust be basic pay."},
                    {"q": "New care workers?", "a": "From 2025, no new overseas care workers unless regulated senior roles.\nExisting workers can extend.\nTransition rules for pre-2025 applicants."},
                    {"q": "English?", "a": "B1 level required.\nTest or academic qualification.\nExemptions for English-speaking countries."},
                    {"q": "Documents?", "a": "CoS, professional registration for regulated roles, English proof.\nCriminal record check mandatory.\nTB and financials if needed."},
                    {"q": "Duration?", "a": "Up to 5 years, extendable.\nPath to ILR after 5 years.\nAnnual updates if salary changes."},
                    {"q": "Dependents?", "a": "Yes, with additional financial requirements.\nDependents can work/study.\nHealth surcharge applies."},
                    {"q": "Switch?", "a": "New CoS for job changes.\nStay within health/care sector for visa validity.\nUpdate Home Office promptly."},
                    {"q": "ILR?", "a": "After 5 years, Life in UK test, B1 English.\nContinuous residence required.\nNo absence limits exceeded."},
                    {"q": "TB?", "a": "Yes for listed countries.\nValid 6 months.\nSubmitted with app."}
                ]
            },
            "Global Business Mobility": {
                "questions": [
                    "Intra-company transfer?",
                    "Senior/specialist employee?",
                    "Salary £73,900+?",
                    "English?",
                    "Sponsor linked company?",
                    "Refusals?",
                    "Duration <3 years?",
                    "Expansion worker?",
                    "Meet points?",
                    "Dependents?"
                ],
                "checklist": [
                    "CoS",
                    "Employment proof",
                    "Passport",
                    "Salary details",
                    "Company link proof",
                    "English",
                    "TB",
                    "Financials",
                    "Previous payroll",
                    "Dependents"
                ],
                "next_steps": "For business expansion.",
                "faqs": [
                    {"q": "Routes?", "a": "Includes Senior or Specialist Worker, Graduate Trainee, UK Expansion Worker, Service Supplier, Secondment Worker.\nEach has specific eligibility.\nTemporary, no settlement path."},
                    {"q": "Salary?", "a": "High thresholds, e.g., £73,900 for senior workers.\nBased on role and experience.\nMust be paid by overseas employer."},
                    {"q": "Duration?", "a": "Up to 3 years for most routes, shorter for some.\nExtensions limited.\nCooling-off after max stay."},
                    {"q": "English?", "a": "B1 level for most routes.\nTest or exemption.\nNot required for short-term service suppliers."},
                    {"q": "Documents?", "a": "CoS, proof of company link, salary evidence, employment history.\nEnglish and TB if applicable.\nSponsor must be linked entity."},
                    {"q": "ILR?", "a": "No path to indefinite leave; temporary only.\nSwitch to other visas possible.\nTime doesn't count towards settlement."},
                    {"q": "Dependents?", "a": "Yes, family can join.\nFinancial maintenance required.\nDependents can work/study."},
                    {"q": "Switch?", "a": "Limited in-route switching.\nNew application for different GBM route.\nTo skilled worker after."},
                    {"q": "TB?", "a": "Yes for longer stays from listed countries.\nValid 6 months.\nFamily too."},
                    {"q": "Expansion?", "a": "For setting up UK branch, up to 2 years.\nLimited numbers per company.\nBusiness plan evidence needed."}
                ]
            },
            "Minister of Religion Visa": {
                "questions": [
                    "Religious worker?",
                    "Sponsor faith body?",
                    "Salary meets min?",
                    "English B2?",
                    "Maintenance funds?",
                    "Refusals?",
                    "Genuine role?",
                    "Meet points?",
                    "Temporary or long?",
                    "Dependents?"
                ],
                "checklist": [
                    "CoS",
                    "Religious proof",
                    "Passport",
                    "Salary details",
                    "Sponsor licence",
                    "English",
                    "TB",
                    "Financials",
                    "Role description",
                    "Dependents"
                ],
                "next_steps": "For religious duties.",
                "faqs": [
                    {"q": "Eligible?", "a": "Ministers, missionaries, members of religious orders.\nSponsor must be licensed faith body.\nRole must be religious, not administrative."},
                    {"q": "Salary?", "a": "Meets national minimum wage or going rate.\nAllowances can count if guaranteed.\nEvidence of payment required."},
                    {"q": "Duration?", "a": "Up to 3 years for temporary, longer for ministers.\nExtensions possible.\nSettlement after 5 years for long-term."},
                    {"q": "English?", "a": "B2 level for ministers.\nLower for temporary workers.\nApproved test or exemption."},
                    {"q": "Documents?", "a": "CoS, role description, sponsor details, English proof.\nReligious qualification or experience.\nTB and criminal check if needed."},
                    {"q": "ILR?", "a": "Possible for long-term religious workers after 5 years.\nLife in UK test required.\nNot for temporary route."},
                    {"q": "Dependents?", "a": "Yes, family can apply.\nFinancial maintenance.\nWork/study allowed."},
                    {"q": "Switch?", "a": "Limited; new application needed.\nFrom visitor possible in cases.\nTo skilled worker if eligible."},
                    {"q": "TB?", "a": "Yes from listed.\nValid test.\nFamily members too."},
                    {"q": "Genuine test?", "a": "Home Office assesses if role is genuine religious work.\nSponsor must confirm duties.\nInterview may be required."}
                ]
            }
        }
    },
    "Study Immigration": {
        "subservices": {
            "Student Visa": {
                "questions": [
                    "Unconditional offer from licensed sponsor?",
                    "English requirement met (B1/B2)?",
                    "Funds for tuition and living (£1,334/month London)?",
                    "Course at degree level or above?",
                    "Previous UK study history?",
                    "Intend to work during studies?",
                    "Previous visa refusals?",
                    "ATAS certificate needed for subject?",
                    "From low-risk country?",
                    "Bringing dependents?"
                ],
                "checklist": [
                    "Valid passport",
                    "Confirmation of Acceptance for Studies (CAS)",
                    "English proficiency proof",
                    "Financial documents (bank statements)",
                    "TB test certificate (if applicable)",
                    "Academic qualifications",
                    "ATAS certificate (if required)",
                    "Scholarship/sponsor consent",
                    "Previous UK visa evidence",
                    "Dependents' documents"
                ],
                "next_steps": "Use CAS to apply online. Attend credibility interview if required.",
                "faqs": [
                    {"q": "Funds needed?", "a": "Full tuition fees plus living costs: £1,334/month for London (up to 9 months), £1,023 elsewhere.\nFunds must be held for 28 days.\nScholarships or official sponsors can reduce amount."},
                    {"q": "English level?", "a": "B2 for degree-level, B1 for below.\nApproved test like IELTS or integrated in CAS.\nExempt if from English-majority country or prior UK study."},
                    {"q": "Work allowed?", "a": "20 hours/week during term for degree-level, 10 for below.\nFull-time during vacations.\nNo self-employment or pro sports."},
                    {"q": "Dependents?", "a": "Only for postgraduate students on courses >9 months.\nFinancial increase for family.\nDependents can work full-time."},
                    {"q": "Documents?", "a": "CAS from sponsor, financial proof, English test, academic transcripts.\nTB certificate if applicable.\nATAS for sensitive subjects."},
                    {"q": "Duration?", "a": "Course length plus 2-4 months extra depending on level.\nExtensions for further study.\nTime limits on total study time."},
                    {"q": "ATAS?", "a": "Required for certain science/engineering subjects with security risks.\nApply online via GOV.UK.\nCAS won't be issued without it."},
                    {"q": "Interview?", "a": "Credibility interview to confirm genuine student.\nQuestions on course, finances, intentions.\nRefusal if not credible."},
                    {"q": "Switch?", "a": "From visitor or short-term study possible.\nIn-UK applications for extensions.\nTo work visa after graduation via graduate route."},
                    {"q": "TB test?", "a": "For stays >6 months from listed countries.\nApproved clinic.\nCertificate submitted with application."}
                ]
            },
            "Child Student Visa": {
                "questions": [
                    "Aged 4-17?",
                    "Offer from independent school?",
                    "Parental consent?",
                    "Funds for fees/living?",
                    "Guardian in UK?",
                    "Previous study?",
                    "Refusals?",
                    "English if needed?",
                    "TB test?",
                    "Intend return?"
                ],
                "checklist": [
                    "Passport",
                    "CAS",
                    "Consent letter",
                    "Financials",
                    "Guardian details",
                    "TB cert",
                    "Academic records",
                    "Accommodation",
                    "Travel plans",
                    "Previous visas"
                ],
                "next_steps": "Apply with guardian arrangements.",
                "faqs": [
                    {"q": "Age?", "a": "For children aged 4-17 studying at independent schools.\nUnder 4 not eligible.\nSwitch to adult student at 18."},
                    {"q": "School type?", "a": "Must be independent fee-paying school with sponsor license.\nState schools not eligible for this visa.\nBoarding or day schools accepted."},
                    {"q": "Funds?", "a": "Full fees plus living costs if needed.\nSponsor or parents provide evidence.\nNo public funds recourse."},
                    {"q": "Guardian?", "a": "Required for under 12; can be relative or appointed.\nOver 12 can be school-accommodated.\nGuardian must be UK-based."},
                    {"q": "Documents?", "a": "CAS, parental consent, financial proof, guardian details.\nPassport and TB if applicable.\nAcademic history."},
                    {"q": "Duration?", "a": "Up to 6 years or course length.\nExtensions possible.\nUntil age 18 max."},
                    {"q": "Work?", "a": "No work allowed.\nFocus on study.\nVoluntary work may be permitted."},
                    {"q": "English?", "a": "Not required as school assesses.\nIntegrated in CAS.\nNo separate test."},
                    {"q": "Switch?", "a": "To adult student visa at 16+.\nIn-UK application possible.\nTo other categories if eligible."},
                    {"q": "TB?", "a": "Yes from listed countries.\nChild-appropriate test.\nValid 6 months."}
                ]
            },
            "Short-term Study Visa": {
                "questions": [
                    "Course <6 months (11 for English)?",
                    "Licensed provider?",
                    "Funds for stay?",
                    "Intend leave after?",
                    "No work?",
                    "Refusals?",
                    "English course?",
                    "TB test?",
                    "From low-risk?",
                    "Recreational study?"
                ],
                "checklist": [
                    "Passport",
                    "Course acceptance",
                    "Financials",
                    "Accommodation",
                    "Return ticket",
                    "TB cert",
                    "Previous study",
                    "Sponsor letter",
                    "Itinerary",
                    "Ties home"
                ],
                "next_steps": "For short courses only.",
                "faqs": [
                    {"q": "Duration?", "a": "Up to 6 months for general courses, 11 for English language.\nNo extensions.\nMust leave at end."},
                    {"q": "Work?", "a": "No work or business activities.\nUnpaid internships may be allowed if part of course.\nVoluntary work limited."},
                    {"q": "Extension?", "a": "No extensions permitted.\nRe-apply from outside UK.\nFrequent applications scrutinized."},
                    {"q": "English?", "a": "No test required; school assesses.\nFor English courses up to 11 months.\nOther courses any subject."},
                    {"q": "Documents?", "a": "Course acceptance letter, financials, accommodation details.\nReturn ticket and home ties.\nTB if long stay."},
                    {"q": "Switch?", "a": "Cannot switch to other visas in UK.\nMust leave and re-apply.\nTime doesn't count for settlement."},
                    {"q": "Dependents?", "a": "No dependents allowed.\nSeparate visitor visas.\nFamily cannot stay long-term."},
                    {"q": "TB?", "a": "For stays over 6 months from listed countries.\nNot for standard 6-month visit.\nApproved clinic."},
                    {"q": "Appeal?", "a": "No appeal rights.\nRe-apply with better evidence.\nAdmin review possible."},
                    {"q": "Processing?", "a": "Usually 3 weeks.\nPriority options available.\nBiometrics required."}
                ]
            }
        }
    },
    "Visit Immigration": {
        "subservices": {
            "Standard Visitor Visa": {
                "questions": [
                    "Visiting for tourism/business/family <6 months?",
                    "Sufficient funds for stay?",
                    "Strong ties to home country?",
                    "Intend to leave after visit?",
                    "Previous UK visa refusals?",
                    "Plan to work or study?",
                    "Medical treatment planned?",
                    "Transiting through UK?",
                    "Have invitation letter?",
                    "TB test required?"
                ],
                "checklist": [
                    "Valid passport with blank page",
                    "Proof of home ties (job letter, property)",
                    "Bank statements/financial proof",
                    "Travel itinerary/flight bookings",
                    "Invitation letter (if visiting family)",
                    "TB test certificate (if applicable)",
                    "Accommodation details",
                    "Return ticket",
                    "Previous travel history",
                    "Sponsor documents if applicable"
                ],
                "next_steps": "Apply online, provide biometrics. No work allowed.",
                "faqs": [
                    {"q": "Stay duration?", "a": "Up to 6 months per visit.\nMultiple entries allowed on multi-visa.\nLong-term visas for frequent visitors up to 10 years."},
                    {"q": "Work allowed?", "a": "Limited business meetings, conferences; no paid work.\nArtists/athletes can perform if unpaid.\nNo job replacement of UK workers."},
                    {"q": "Funds proof?", "a": "Bank statements showing sufficient for trip without public funds.\nSponsor can provide if evidenced.\nNo fixed amount, assessed case-by-case."},
                    {"q": "Ties to home?", "a": "Job letter, property deeds, family commitments.\nTo show intention to return.\nWeak ties often lead to refusal."},
                    {"q": "Documents?", "a": "Passport, itinerary, financials, invitation if applicable.\nHome ties proof essential.\nTranslations for non-English docs."},
                    {"q": "Extension?", "a": "Up to 6 months total for medical or exceptional reasons.\nApply in UK before expiry.\nRarely granted for tourism."},
                    {"q": "Dependents?", "a": "Family apply separately.\nNo dependent visa; all as visitors.\nChildren need consent if not traveling with both parents."},
                    {"q": "TB test?", "a": "For stays over 6 months from listed countries.\nNot for standard 6-month visit.\nApproved clinic."},
                    {"q": "Appeal?", "a": "No appeal right; admin review or re-apply.\nHuman rights claim in rare cases.\nLegal advice for complex refusals."},
                    {"q": "Processing?", "a": "3 weeks standard.\nPriority 5 days, super priority next day.\nVaries by country."}
                ]
            },
            "Marriage Visitor Visa": {
                "questions": [
                    "Intend to marry/civil partnership in UK?",
                    "Leave after 6 months?",
                    "Funds for stay?",
                    "No settlement intent?",
                    "Refusals?",
                    "Partner details?",
                    "Ceremony booked?",
                    "TB test?",
                    "Ties home?",
                    "Genuine?"
                ],
                "checklist": [
                    "Passport",
                    "Marriage plans",
                    "Financials",
                    "Accommodation",
                    "Return ticket",
                    "TB cert",
                    "Partner docs",
                    "Invitation",
                    "Ties proof",
                    "Previous marriages"
                ],
                "next_steps": "For marriage, not settlement.",
                "faqs": [
                    {"q": "Duration?", "a": "6 months maximum stay.\nMust marry within this time.\nNo extension for marriage purposes."},
                    {"q": "Work?", "a": "No work or study allowed.\nFocus on marriage only.\nBusiness activities prohibited."},
                    {"q": "Switch to spouse?", "a": "No in-UK switch; must leave and apply for spouse visa.\nFiancé visa alternative for settlement intent.\nPlan accordingly to avoid issues."},
                    {"q": "Documents?", "a": "Proof of marriage plans like venue booking, financials, return ticket.\nPartner details and relationship evidence.\nHome ties to show departure intent."},
                    {"q": "Appeal?", "a": "No standard appeal; re-apply or judicial review.\nHuman rights if applicable.\nCommon refusals on intent."},
                    {"q": "TB?", "a": "If stay over 6 months, from listed countries.\nUsually not for 6-month visa.\nCheck GOV.UK list."},
                    {"q": "Processing?", "a": "3 weeks standard.\nPriority available.\nBiometrics appointment required."},
                    {"q": "Biometrics?", "a": "Yes, at visa center.\nFingerprint and photo.\nPart of application process."},
                    {"q": "Partner visa?", "a": "Separate spouse visa for settlement after marriage.\nDifferent requirements like financial.\nApply from home country."},
                    {"q": "Genuine?", "a": "Evidence of real intent to marry, not immigration evasion.\nInterview may probe relationship.\nRefusals if doubted."}
                ]
            },
            "Transit Visa": {
                "questions": [
                    "Transiting UK to another country?",
                    "No entry intent?",
                    "Onward ticket?",
                    "Visa for destination?",
                    "Refusals?",
                    "Landside or airside?",
                    "TB test?",
                    "Funds?",
                    "Genuine transit?",
                    "Frequent traveler?"
                ],
                "checklist": [
                    "Passport",
                    "Onward ticket",
                    "Destination visa",
                    "Financials",
                    "Itinerary",
                    "TB cert if long",
                    "Previous travel",
                    "Accommodation if landside",
                    "Sponsor if needed",
                    "Ties"
                ],
                "next_steps": "For passing through.",
                "faqs": [
                    {"q": "Needed?", "a": "Depends on nationality and transit type.\nVisa nationals need unless exempt.\nCheck GOV.UK checker."},
                    {"q": "Airside?", "a": "No need to pass immigration if not leaving airport.\nValid for 24-48 hours.\nOnward flight confirmed."},
                    {"q": "Landside?", "a": "Visa required to leave airport, e.g., hotel stay.\nProof of onward travel essential.\nFunds and ties checked."},
                    {"q": "Documents?", "a": "Onward ticket, destination visa if needed, passport.\nItinerary and purpose.\nNo extensive financials usually."},
                    {"q": "Duration?", "a": "48 hours for direct airside transit.\n24 hours for visitor in transit.\nNo extensions."},
                    {"q": "Work?", "a": "No activities allowed.\nPure transit only.\nNo meetings or tourism."},
                    {"q": "Appeal?", "a": "No appeal; re-apply.\nAdmin review possible.\nRare refusals if docs complete."},
                    {"q": "TB?", "a": "Rarely required for short transit.\nOnly if extended stay.\nCheck if country listed."},
                    {"q": "Processing?", "a": "3 weeks standard.\nSame as visitor.\nBiometrics needed."}
                ]
            }
        }
    },
    "Settlement": {
        "subservices": {
            "Indefinite Leave to Remain (ILR)": {
                "questions": [
                    "5+ years in qualifying visa route?",
                    "English test passed (B1)?",
                    "Passed Life in the UK test?",
                    "Continuous residence no breaks >180 days?",
                    "Good character no criminality?",
                    "Previous refusals or overstays?",
                    "Financial independence if required?",
                    "Bringing dependents?",
                    "Route-specific requirements met?",
                    "Knowledge of Language and Life (KoLL) satisfied?"
                ],
                "checklist": [
                    "Current passport and previous ones",
                    "Biometric residence permit",
                    "English language certificate",
                    "Life in the UK test pass certificate",
                    "Proof of continuous residence (P60s, letters)",
                    "Good character documents",
                    "Financial proof if applicable",
                    "Dependents' documents",
                    "Route-specific evidence (e.g., payslips for work)",
                    "TB test if recently arrived"
                ],
                "next_steps": "Apply online for ILR. Attend biometrics. Note 2025 changes if applicable.",
                "faqs": [
                    {"q": "Qualifying period?", "a": "5 years in most routes like work or family.\n2-3 years for some like investors.\nContinuous with no excessive absences."},
                    {"q": "English level?", "a": "B1 speaking and listening.\nApproved test or degree in English.\nExempt if over 65 or disability."},
                    {"q": "Life in UK test?", "a": "Required for ages 18-65.\nBook online, 24 questions on UK life.\nPass certificate valid indefinitely."},
                    {"q": "Absences allowed?", "a": "Less than 180 days per year.\nTotal under 540 days in 5 years.\nExceptions for work or compelling reasons."},
                    {"q": "Documents?", "a": "Residence proof like P60s, utility bills; English and Life test.\nPassports showing travel.\nRoute-specific like salary for work."},
                    {"q": "Good character?", "a": "No criminal convictions or immigration violations.\nDeclare all issues.\nTax and bankruptcy issues considered."},
                    {"q": "Dependents?", "a": "Can apply jointly or separately.\nSame requirements.\nChildren under 18 automatic if parents settle."},
                    {"q": "Fee?", "a": "High, around £2,885 per person.\nCheck GOV.UK for current.\nBiometrics included."},
                    {"q": "Processing?", "a": "Up to 6 months.\nPriority service available.\nDecision letter sent."},
                    {"q": "Appeal?", "a": "Admin review within 28 days.\nJudicial review if errors.\nRe-apply if fixable issues."}
                ]
            },
            "EU Settlement Scheme": {
                "questions": [
                    "EU/EEA citizen or family?",
                    "Lived in UK before 31 Dec 2020?",
                    "Continuous 5 years for settled?",
                    "Pre-settled status held?",
                    "Good character?",
                    "Refusals?",
                    "Evidence of residence?",
                    "Dependents?",
                    "Late application grounds?",
                    "Digital status?"
                ],
                "checklist": [
                    "Passport/ID",
                    "Proof of residence (bills, P60)",
                    "EU Settlement app evidence",
                    "Character docs",
                    "Dependents proof",
                    "Relationship evidence",
                    "Previous status",
                    "Biometrics if needed",
                    "TB if applicable",
                    "App screenshot"
                ],
                "next_steps": "Upgrade from pre-settled if eligible.",
                "faqs": [
                    {"q": "Deadline?", "a": "Passed June 2021, but late applications with reasonable grounds accepted.\nGrounds like illness or lack of awareness.\nApply via app or paper if complex."},
                    {"q": "Settled vs pre?", "a": "Settled for 5+ years continuous residence.\nPre-settled for less, valid 5 years.\nUpgrade when 5 years reached."},
                    {"q": "Evidence?", "a": "Automated checks via HMRC/DWP for UK residents.\nAlternative like bank statements or bills.\nOne per month for period."},
                    {"q": "Family?", "a": "Joining family members apply separately.\nRelationship pre-2021.\nDurably resident rules."},
                    {"q": "Documents?", "a": "ID document, residence proof if automated fails.\nDigital status via app.\nNo physical card."},
                    {"q": "Appeal?", "a": "Yes, within 28 days.\nFree for scheme refusals.\nIndependent tribunal."},
                    {"q": "Processing?", "a": "Varies, usually weeks.\nComplex cases longer.\nStatus while pending."},
                    {"q": "Biometrics?", "a": "Via app for most.\nOverseas centers if needed.\nReuse from previous."},
                    {"q": "Absences?", "a": "Up to 5 years break for settled.\n2 years for pre-settled.\nCOVID exceptions."},
                    {"q": "Rights?", "a": "Work, study, NHS access.\nEqual to citizens.\nNo voting."}
                ]
            }
        }
    },
    "Citizenship": {
        "subservices": {
            "Naturalisation": {
                "questions": [
                    "Hold ILR/settled status?",
                    "Lived in UK 5 years (3 if married to British)?",
                    "Good character?",
                    "English B1 and Life in UK passed?",
                    "Intend to live in UK?",
                    "Previous refusals or citizenship issues?",
                    "Dual citizenship allowed in home country?",
                    "Age 18+?",
                    "Mental capacity?",
                    "Referees provided?"
                ],
                "checklist": [
                    "Current and previous passports",
                    "ILR proof (BRP)",
                    "Good character evidence (police cert if needed)",
                    "English certificate",
                    "Life in the UK pass",
                    "Residence proof for qualifying period",
                    "Two referee declarations",
                    "Biometrics enrollment",
                    "Fee payment receipt",
                    "Marriage certificate if name change"
                ],
                "next_steps": "Apply online, attend ceremony if approved.",
                "faqs": [
                    {"q": "Residence req?", "a": "5 years with ILR, or 3 if spouse of British citizen.\nNo more than 450 days absence, 90 in last year.\nExceptions for crown service or compelling reasons."},
                    {"q": "Absences?", "a": "Max 450 days in 5 years, 90 in final year.\nDocument reasons for longer absences.\nCOVID-related leniency in some cases."},
                    {"q": "Good character?", "a": "No serious or recent crimes, declare all.\nImmigration compliance checked.\nTax and bankruptcy issues considered."},
                    {"q": "Tests?", "a": "B1 English and Life in the UK test.\nExempt if over 65 or medical condition.\nTests valid indefinitely."},
                    {"q": "Documents?", "a": "ILR proof, residence evidence, referees (professional).\nPassports for travel history.\nTranslations if needed."},
                    {"q": "Fee?", "a": "Around £1,580 application plus ceremony.\nNo refund if refused.\nBiometrics included."},
                    {"q": "Processing?", "a": "Up to 6 months.\nBiometrics appointment.\nDecision letter."},
                    {"q": "Ceremony?", "a": "Oath of allegiance at local council.\nWithin 3 months of approval.\nReceive certificate."},
                    {"q": "Dual?", "a": "UK allows dual citizenship.\nCheck home country rules.\nNo renunciation required."},
                    {"q": "Appeal?", "a": "No appeal; re-apply or judicial review.\nRefund minus admin fee.\nCommon refusals on good character."}
                ]
            },
            "Registration as British Citizen": {
                "questions": [
                    "Eligible by birth/descent?",
                    "Parent British?",
                    "Born in UK to settled parents?",
                    "Under 18?",
                    "Good character if 10+?",
                    "Refusals?",
                    "Intend live in UK?",
                    "Dual ok?",
                    "Discretion needed?",
                    "Documents ready?"
                ],
                "checklist": [
                    "Birth certificate",
                    "Parent's citizenship proof",
                    "Passport",
                    "Good character if applicable",
                    "Consent if minor",
                    "Residence proof",
                    "Referees if needed",
                    "Fee receipt",
                    "Biometrics",
                    "Marriage cert parents"
                ],
                "next_steps": "For children or descent.",
                "faqs": [
                    {"q": "Who qualifies?", "a": "By descent if parent British at birth.\nBy birth in UK to settled/British parent.\nDiscretionary for minors."},
                    {"q": "Fee?", "a": "Lower for children, around £1,012.\nAdult £1,351.\nBiometrics included."},
                    {"q": "Processing?", "a": "Up to 6 months.\nBiometrics if needed.\nCertificate issued."},
                    {"q": "Tests?", "a": "No English or Life test for registration.\nOnly for naturalisation.\nGood character for over 10."},
                    {"q": "Documents?", "a": "Birth cert, parent's citizenship evidence, consent for minors.\nResidence if applicable.\nReferees for adults."},
                    {"q": "Appeal?", "a": "No; re-apply or review.\nRare refusals.\nLegal challenge if error."},
                    {"q": "Biometrics?", "a": "Yes for most over 5.\nAt center or app.\nPart of process."},
                    {"q": "Ceremony?", "a": "No ceremony for registration.\nOnly naturalisation.\nCertificate by post."},
                    {"q": "Dual?", "a": "Allowed in UK.\nCheck other country.\nNo issue."},
                    {"q": "Adults?", "a": "Discretionary if missed childhood registration.\nGood character required.\nResidence evidence."}
                ]
            }
        }
    },
    "Asylum and Protection": {
        "subservices": {
            "Asylum Claim": {
                "questions": [
                    "Fear of persecution in home country?",
                    "Persecution based on race/religion/politics/group/opinion?",
                    "Claimed asylum at first safe opportunity?",
                    "Evidence of threat (documents/witnesses)?",
                    "Previous UK visa refusals or deportations?",
                    "Applying for family reunion?",
                    "Victim of human trafficking/modern slavery?",
                    "Stateless person?",
                    "Eligible for resettlement scheme?",
                    "Bringing dependents?"
                ],
                "checklist": [
                    "Passport or travel document (if available)",
                    "Evidence of persecution (photos, reports, statements)",
                    "Travel history documents",
                    "Biometrics enrollment",
                    "Witness statements or affidavits",
                    "Medical reports (if torture/trauma)",
                    "Country information reports",
                    "Family relationship documents",
                    "Previous immigration decisions",
                    "TB test if required"
                ],
                "next_steps": "Claim at port or in-UK office. Seek legal aid immediately.",
                "faqs": [
                    {"q": "Processing time?", "a": "Up to 6 months for straightforward claims, longer for complex.\nPriority for vulnerable.\nUpdates via Home Office portal."},
                    {"q": "Work allowed?", "a": "After 12 months if delay not your fault, in shortage occupations.\nVoluntary work anytime.\nNo self-employment."},
                    {"q": "Accommodation?", "a": "Provided if destitute, dispersal across UK.\nSupport £40/week per person.\nLegal aid for appeals."},
                    {"q": "Dependents?", "a": "Included in main claim if family.\nSeparate if arriving later.\nRights same as main applicant."},
                    {"q": "Documents?", "a": "Evidence key: statements, photos, reports.\nID if available.\nTranslations required."},
                    {"q": "Appeal?", "a": "Yes if refused, to First-tier Tribunal.\nLegal aid available.\nFurther appeals possible."},
                    {"q": "Interview?", "a": "Substantive interview on claim details.\nPrepare with lawyer.\nInterpreter provided."},
                    {"q": "Legal aid?", "a": "Available for asylum claims.\nMerits and means tested.\nNGOs like Refugee Council help."},
                    {"q": "Safe third country?", "a": "May be removed if passed through safe country.\nDublin-like rules post-Brexit.\nChallenges on human rights."},
                    {"q": "Status if granted?", "a": "Refugee status for 5 years, then review.\nProtection route if not convention refugee.\nPath to settlement."}
                ]
            },
            "Refugee Family Reunion": {
                "questions": [
                    "Granted refugee/HP status?",
                    "Pre-flight family?",
                    "Spouse/children under 18?",
                    "No public funds recourse?",
                    "Accommodation available?",
                    "Refusals?",
                    "Genuine relationship?",
                    "Funds?",
                    "TB test for family?",
                    "Exceptional circumstances?"
                ],
                "checklist": [
                    "Status proof",
                    "Marriage/birth certs",
                    "Relationship evidence",
                    "Accommodation proof",
                    "Financial if needed",
                    "TB certs",
                    "Passports",
                    "Previous decisions",
                    "DNA if required",
                    "Sponsor undertaking"
                ],
                "next_steps": "Apply for family to join.",
                "faqs": [
                    {"q": "Who qualifies?", "a": "Pre-existing spouse/partner and children under 18.\nPost-flight family in exceptional cases.\nNo fee, but evidence strict."},
                    {"q": "Fee?", "a": "Free application.\nBiometrics may have cost overseas.\nLegal aid available."},
                    {"q": "Processing?", "a": "6 months average.\nPriority for vulnerable.\nTrack via VFS or Home Office."},
                    {"q": "Documents?", "a": "Relationship proof like marriage/birth certs, photos.\nSponsor's status.\nDNA if relationship doubted."},
                    {"q": "Appeal?", "a": "Yes, human rights grounds.\nTo tribunal.\nLegal representation advised."},
                    {"q": "TB?", "a": "Yes for family from listed countries.\nApproved test.\nSubmitted with app."},
                    {"q": "Accommodation?", "a": "Sponsor provides without public funds.\nEvidence like tenancy.\nNo min size, but adequate."},
                    {"q": "Funds?", "a": "No minimum threshold.\nSponsor shows maintenance ability.\nPublic funds access after arrival."},
                    {"q": "Adults?", "a": "Exceptional for over 18 children if dependent/vulnerable.\nCompassionate circumstances.\nRare approvals."},
                    {"q": "DNA?", "a": "If doubt on relationship, Home Office may request.\nVoluntary but refusal impacts.\nCosts reimbursed if positive."}
                ]
            }
        }
    },
    "Specialist Visas": {
        "subservices": {
            "Global Talent Visa": {
                "questions": [
                    "Exceptional talent or promise in field (science, arts, tech)?",
                    "Endorsement from approved body (e.g., Tech Nation)?",
                    "English requirement met?",
                    "Maintenance funds (£1,270)?",
                    "Previous refusals?",
                    "Intend to work in endorsed field?",
                    "Digital technology applicant?",
                    "Arts/culture field?",
                    "Science/research?",
                    "Bringing dependents?"
                ],
                "checklist": [
                    "Passport",
                    "Endorsement letter from body",
                    "English proof if required",
                    "Financial documents",
                    "CV/portfolio/evidence of talent",
                    "Recommendation letters",
                    "TB test",
                    "Field-specific evidence",
                    "Previous UK visas",
                    "Dependents docs"
                ],
                "next_steps": "Apply after endorsement. No job offer needed.",
                "faqs": [
                    {"q": "Endorsing bodies?", "a": "Tech Nation for digital, Arts Council for arts, UKRI for science/research, Royal Society etc.\nApply for endorsement first.\nPromise for early career, talent for established."},
                    {"q": "English?", "a": "Not required for endorsement stage.\nB1 for visa if not exempt.\nDegree in English suffices."},
                    {"q": "Funds?", "a": "£1,270 maintenance for 28 days.\nOr employer guarantee.\nDependents additional."},
                    {"q": "Duration?", "a": "5 years initial.\nExtendable.\nSettlement after 3 for talent, 5 for promise."},
                    {"q": "Documents?", "a": "Endorsement letter, CV, recommendation letters, portfolio.\nFinancial proof, TB.\nNo job offer needed."},
                    {"q": "ILR?", "a": "After 3 years for exceptional talent.\n5 for promise.\nLife test and English."},
                    {"q": "Dependents?", "a": "Yes, family can apply.\nWork/study allowed.\nHealth surcharge."},
                    {"q": "Work?", "a": "Flexible work in field.\nSelf-employment ok.\nNo public funds."},
                    {"q": "Switch?", "a": "From other visas if endorsed.\nIn-UK application possible.\nTo skilled worker if needed."},
                    {"q": "TB?", "a": "Yes from listed countries.\nFor main and dependents.\nValid test."}
                ]
            },
            "UK Ancestry Visa": {
                "questions": [
                    "Grandparent born in UK?",
                    "Commonwealth citizen?",
                    "Intend work and maintain self?",
                    "Funds for stay?",
                    "Refusals?",
                    "Age 17+?",
                    "TB test?",
                    "English?",
                    "Dependents?",
                    "Genuine ancestry?"
                ],
                "checklist": [
                    "Passport",
                    "Grandparent birth cert",
                    "Parent birth cert",
                    "Financials",
                    "Job offer if any",
                    "TB cert",
                    "Accommodation",
                    "Ancestry proof",
                    "Previous visas",
                    "Dependents"
                ],
                "next_steps": "For Commonwealth with UK ancestry.",
                "faqs": [
                    {"q": "Eligibility?", "a": "Grandparent born in UK or islands.\nCommonwealth citizen.\nAble to work and support self."},
                    {"q": "Work?", "a": "Yes, any employment or self-employment.\nNo restrictions.\nStudy also allowed."},
                    {"q": "Duration?", "a": "5 years initial.\nExtendable.\nSettlement after 5."},
                    {"q": "English?", "a": "No requirement for entry.\nB1 for settlement.\nLife test too."},
                    {"q": "Documents?", "a": "Birth certificates showing ancestry, passport, financial proof.\nTB if applicable.\nNo job offer needed."},
                    {"q": "ILR?", "a": "After 5 years residence.\nEnglish and Life test.\nGood character."},
                    {"q": "Dependents?", "a": "Yes, partner/children.\nFinancial maintenance.\nWork/study ok."},
                    {"q": "TB?", "a": "From listed countries.\nValid 6 months.\nFor all applicants."},
                    {"q": "Processing?", "a": "3 weeks standard.\nPriority available.\nBiometrics required."},
                    {"q": "Extension?", "a": "Yes, online in UK.\nSame requirements.\nBefore expiry."}
                ]
            },
            "Innovator Founder Visa": {
                "questions": [
                    "Innovative, viable, scalable business?",
                    "Endorsed by approved body?",
                    "English B1?",
                    "Funds £1,270?",
                    "Refusals?",
                    "New business?",
                    "Day-to-day involvement?",
                    "Meet points?",
                    "Dependents?",
                    "Growth plan?"
                ],
                "checklist": [
                    "Passport",
                    "Endorsement",
                    "Business plan",
                    "English",
                    "Financials",
                    "TB",
                    "CV",
                    "Market research",
                    "Previous businesses",
                    "Dependents"
                ],
                "next_steps": "For starting business.",
                "faqs": [
                    {"q": "Endorsers?", "a": "Approved bodies like accelerators or universities.\nAssess innovation, viability, scalability.\nEndorsement first step."},
                    {"q": "Funds?", "a": "£1,270 maintenance.\nBusiness funds separate.\nSponsor guarantee possible."},
                    {"q": "Duration?", "a": "3 years initial.\nExtendable if milestones met.\nSettlement after 3 if successful."},
                    {"q": "English?", "a": "B1 level.\nTest or exemption.\nRequired for application."},
                    {"q": "Documents?", "a": "Endorsement, business plan, CV, market research.\nEnglish and financials.\nTB if needed."},
                    {"q": "ILR?", "a": "After 3 years if business succeeds.\nGrowth criteria like jobs/revenue.\nEnglish and Life test."},
                    {"q": "Dependents?", "a": "Yes, family join.\nWork/study allowed.\nAdditional funds."},
                    {"q": "Work?", "a": "Must work on own business.\nNo other employment.\nDay-to-day involvement."},
                    {"q": "Switch?", "a": "From start-up visa possible.\nIn-UK application.\nTo skilled if business changes."},
                    {"q": "TB?", "a": "Yes from listed.\nValid test.\nFor all."}
                ]
            },
            "High Potential Individual Visa": {
                "questions": [
                    "Degree from top global university last 5 years?",
                    "English B1?",
                    "Funds £1,270?",
                    "Refusals?",
                    "Intend work/study?",
                    "Degree eligible?",
                    "TB test?",
                    "Dependents?",
                    "No job needed?",
                    "Genuine?"
                ],
                "checklist": [
                    "Passport",
                    "Degree certificate",
                    "English",
                    "Financials",
                    "TB",
                    "Transcript",
                    "University list proof",
                    "Previous visas",
                    "Dependents",
                    "Intent statement"
                ],
                "next_steps": "For elite graduates.",
                "faqs": [
                    {"q": "Universities?", "a": "Top 50 in at least two global rankings.\nList on GOV.UK, updated yearly.\nDegree within last 5 years."},
                    {"q": "Duration?", "a": "2 years for bachelors/masters, 3 for PhD.\nNo extension.\nSwitch to other visas."},
                    {"q": "Work?", "a": "Yes, any except professional sport/coach.\nSelf-employment allowed.\nNo job offer needed."},
                    {"q": "English?", "a": "B1 level unless degree in English.\nApproved test.\nExemptions listed."},
                    {"q": "Documents?", "a": "Degree certificate, transcript, university confirmation.\nFinancials £1,270, English.\nTB if applicable."},
                    {"q": "Extension?", "a": "No direct extension.\nSwitch to skilled worker etc.\nTime doesn't count for ILR."},
                    {"q": "Dependents?", "a": "No dependents allowed.\nSeparate visas needed.\nFamily apply independently."},
                    {"q": "Switch?", "a": "To work, start-up, or study visas.\nIn-UK possible.\nGraduate route alternative."},
                    {"q": "TB?", "a": "Yes from listed countries.\nValid 6 months.\nSubmitted with app."}
                ]
            }
        }
    }
}

# EMOJI for categories
EMOJI = {
    "Family Immigration": "👪",
    "Work Immigration": "💼",
    "Study Immigration": "🎓",
    "Visit Immigration": "✈️",
    "Settlement": "🏠",
    "Citizenship": "🇬🇧",
    "Asylum and Protection": "🛡️",
    "Specialist Visas": "🌟"
}

# Static Text
T = {
    "welcome": "🌟 *Welcome to Premium ImmigrationBot!* 🚀\nAssisting with UK visas (2025 rules). *Disclaimer:* Not legal advice - consult a lawyer.\n\nQuick, accurate guidance to save your time!",
    "select_category": "📂 Service Categories",
    "choose_category": "Select a category below:",
    "select_sub": "💼 Sub-Services",
    "choose_sub": "Select a service in {cat}:",
    "elig_intro": "📝 *Eligibility Assessment for {srv}* (Time-saving triage)",
    "elig_progress": "Question {curr}/{total}: ",
    "invalid": "⚠️ *Invalid input.* Please use the buttons or type correctly.",
    "ask_name": "👤 *Enter your full name:*",
    "ask_email": "📧 *Enter your email:*",
    "bad_email": "⚠️ *Invalid email,* try again.",
    "ask_phone": "📞 *Enter phone with country code:*",
    "ask_urgency": "⏰ *Urgency level?*",
    "doclist": "📑 *Personalized Document Checklist for {srv}:* \n{list}",
    "email_docs": "Please send all the listed docs to solicitors@hotmail.co.uk",
    "faq_header": "❓ FAQs for {srv}",
    "faq_body": "Select a question:",
    "faq_answer": "*Q:* {q}\n*A:* {a}",
    "anything_else": "Anything else I can help with, {name}?",
    "thank_you": "Hello {name}, our team will contact you soonest.",
    "start_new": "Start Again",
    "fallback": "⚠️ *Sorry, didn't catch that.* Type 'menu' to restart or ask clearly.",
    "llm_disc": "\n\n_(This is AI-generated reference only; always verify with a professional lawyer.)_",
    "ask_question": "What else can I help with regarding the {srv} visa, {name}?"
}

HDRS = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}

def ws(payload):
    try:
        response = requests.post(WA_URL, headers=HDRS, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Message sent successfully: {response.json()}")
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")

# Global send_action_buttons function (moved from inside send_text)
def send_action_buttons(to, case_id, intake_url, upload_url, folder_url):
    payload = {
        "messaging_product":"whatsapp",
        "to": to,
        "type":"interactive",
        "interactive":{
            "type":"button",
            "header":{"type":"text","text":"✅ Case registered"},
            "body":{"text": f"Case ID: *{case_id}*\nChoose an action:"},
            "action":{"buttons":[
                {"type":"url","url": intake_url, "title":"📝 Intake form"},
                {"type":"url","url": upload_url, "title":"📄 Upload docs"},
                {"type":"url","url": folder_url, "title":"📁 Case folder"},
            ]}
        }
    }
    ws(payload)


def send_text(to, body):
    ws({"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}})

def send_buttons(to, body, opts):
    opts = opts[:3]
    ws({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body[:1024]},
            "action": {"buttons": [{"type": "reply", "reply": {"id": i, "title": t[:20]}} for i, t in opts]}
        }
    })

def send_list(to, header, body, btn, rows):
    rows = rows[:10]
    action = {"button": btn[:20], "sections": [{"title": "Options"[:20], "rows": [{"id": i, "title": t[:24], "description": d[:72]} for i, t, d in rows]}]}
    ws({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header[:60]},
            "body": {"text": body[:1024]},
            "action": action
        }
    })

# NEW: safe list with numeric fallback (prevents silent UI drop)
def send_list_safe(to, header, body, btn, rows, fallback_tag=None):
    if not rows:
        send_text(to, "No options are available right now. Please try again later.")
        return False
    header = (header or "")[:WALIM["header"]]
    body   = (body or "")[:WALIM["body"]]
    btn    = (btn or "Select")[:WALIM["button"]]
    rows   = rows[:WALIM["rows"]]
    norm_rows = []
    for i, t, d in rows:
        norm_rows.append({
            "id": i,
            "title": (t or "")[:WALIM["list_title"]],
            "description": (d or "")[:WALIM["list_desc"]],
        })
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": header},
            "body": {"text": body},
            "action": {"button": btn, "sections": [{"title": "Options", "rows": norm_rows}]}
        }
    }
    try:
        r = requests.post(WA_URL, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, json=payload, timeout=15)
        if r.status_code == 200:
            sessions.setdefault(to, {}).setdefault("_fallback", {})[fallback_tag or ""] = {"mode": "list", "rows": [(i, t, d) for (i, t, d) in rows]}
            return True
        else:
            print("WA list error:", r.text)
    except Exception as e:
        print("WA list exception:", e)

    # Fallback numbered menu
    numbered = "\n".join([f"{idx}. {t}" for idx, (_, t, _) in enumerate(rows, start=1)])
    send_text(to, f"{header}\n\n{body}\n\n{numbered}\n\nPlease reply with the number or the name.")
    sessions.setdefault(to, {}).setdefault("_fallback", {})[fallback_tag or ""] = {"mode": "numbered", "rows": [(i, t, d) for (i, t, d) in rows]}
    return False

def ask_llm(q, ctx):
    try:
        resp = requests.post(OPENROUTER_API, headers={"Authorization": f"Bearer {OPENROUTER_KEY}"}, json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You are a specialised UK immigration solicitor. Provide accurate, professional advice based on 2025 rules."},
                {"role": "user", "content": f"Context: {ctx}\nQ: {q}"}
            ]
        }, timeout=15)
        if resp.status_code == 200:
            ans = resp.json()["choices"][0]["message"]["content"].strip()
            return ans + T["llm_disc"]
    except:
        pass
    return "Sorry, couldn't fetch info." + T["llm_disc"]

sessions = {}

def reset(uid):
    sessions[uid] = {"state": "cat", "cat": None, "sub": None, "q_idx": 0, "ans": {}, "info": {}, "case": str(uuid.uuid4()), "complex": False, "score": 0,"registered": False}
    
app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return 'OK', 200

# ---------- Apps Script helpers ----------
def call_apps_script(payload, timeout=30):
    try:
        # ensure explicit action so the script routes correctly
        payload = dict(payload or {})
        payload.setdefault("action", "register")

        r = requests.post(APPSCRIPT_URL,
                          headers={"Content-Type": "application/json"},
                          json=payload,
                          timeout=timeout)

        text = r.text
        code = r.status_code

        # Common failure: Web App not deployed “Anyone” → HTML login page
        if "Authorization is required" in text or "<html" in text.lower():
            return {"status": "error",
                    "message": "Apps Script not public (Deploy as Web App → Execute as Me, Who has access: Anyone).",
                    "http": code, "body": text[:200]}

        # Try JSON
        try:
            return r.json()
        except Exception as je:
            return {"status": "error",
                    "message": f"Non-JSON from Apps Script ({code})",
                    "body": text[:300]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ---------- Case registration (to your new Apps Script) ----------
def send_to_case_management(uid, s):
    """
    Registers the case in Apps Script exactly once and returns case_id.
    Also sends clean URL buttons (no long links in text).
    """
    if s.get("case_registered"):
        return s.get("case")

    payload = {
        "name": s['info'].get('Name', ''),
        "email": s['info'].get('Email', ''),
        "phone": s['info'].get('Phone', ''),
        "phoneNumber": uid,  # WhatsApp user ID
        "visaRoute": s.get('sub', ''),
        "urgency": s['info'].get('Urgency', 'Normal'),
        "evidenceChecklist": SERVICES[s['cat']]['subservices'][s['sub']]['checklist'],
        "notes": s.get('notes', '')
    }

    try:
        r = requests.post(APPSCRIPT_URL, json=payload, timeout=20)
        j = r.json()
    except Exception as e:
        print("register error:", e)
        send_text(uid, "⚠️ We couldn’t auto-register your case. We’ll follow up by email.")
        return None

    if j.get("status") in ("success","ok"):
        case_id = j.get("caseId") or s.get("case") or str(uuid.uuid4())
        # Accept either flat keys or a 'buttons' dict from Apps Script
        intake = j.get("intakeFormLink") or j.get("buttons", {}).get("intake", "")
        upload = j.get("uploadDocsLink") or j.get("buttons", {}).get("upload", "")
        folder = j.get("driveFolderLink") or j.get("caseFolderLink") or j.get("buttons", {}).get("folder", "")

        s["case"] = case_id
        s["case_registered"] = True

        send_text(uid, "✅ Your case has been registered.")
        send_action_buttons(uid, case_id, intake, upload, folder)
        return case_id

    send_text(uid, "⚠️ We couldn’t auto-register your case. We’ll follow up by email.")
    return None

# ---------- Media upload pipeline ----------
def _wa_headers(): return {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def _get_media_meta(media_id):
    try:
        r = requests.get(f"{GRAPH_BASE}/{media_id}", headers=_wa_headers(), timeout=20)
        r.raise_for_status()
        j = r.json()
        return j.get("url"), j.get("mime_type"), int(j.get("file_size", 0))
    except Exception as e:
        print("media meta error:", e)
        return None, None, 0

def _download_media(url):
    try:
        r = requests.get(url, headers=_wa_headers(), timeout=120)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print("media download error:", e)
        return None

def _upload_to_drive(uid, case_id, filename, mime, content_b64):
    payload = {
        "action": "upload_media",
        "uid": uid,
        "case_id": case_id,
        "filename": filename,
        "mime": mime or "application/octet-stream",
        "folderId": DRIVE_FOLDER_ID,
        "base64": content_b64
    }
    return call_apps_script(payload, timeout=90)

def handle_media_anytime(uid, msg):
    s = sessions.get(uid) or {}
    case_id = s.get("case") or str(uuid.uuid4())
    sessions.setdefault(uid, s)["case"] = case_id

    mtype = msg.get("type")
    media = msg.get(mtype, {})
    mid   = media.get("id")
    if not mid:
        return
    url, mime, size = _get_media_meta(mid)
    if not url:
        return
    if size and size > MAX_MEDIA_BYTES:
        send_text(uid, f"⚠️ File too large. Please keep under ~{int(MAX_MEDIA_BYTES/1024/1024)} MB or email it.")
        return

    content = _download_media(url)
    if not content:
        send_text(uid, "Sorry, could not fetch the file from WhatsApp. Please resend.")
        return

    b64 = base64.b64encode(content).decode("utf-8")
    name = media.get("filename") or f"{mtype}_{mid}"
    up = _upload_to_drive(uid, case_id, name, mime, b64)
    if up and up.get("status") == "ok":
        link = up.get("url") or up.get("drive_url") or ""
        sessions.setdefault(uid, {}).setdefault("docs", []).append({"name": name, "url": link})
        send_text(uid, f"✅ File saved. {('🔗 '+link) if link else ''}")
    else:
        send_text(uid, "Sorry, we couldn’t save that file. Please try again or email it.")

# ---------- Duplicate check + DOB ----------
DOB_RE = re.compile(r"^(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})$")
def parse_dob(s):
    m = DOB_RE.match((s or "").strip())
    if not m: return None
    d, mth, y = map(int, m.groups())
    try:
        return datetime(y, mth, d).strftime("%Y-%m-%d")
    except: return None

def check_duplicate_in_sheet(name, dob):
    resp = call_apps_script({"action": "fuzzy_duplicate", "name": name, "dob": dob})
    if isinstance(resp, dict) and resp.get("status") == "ok" and resp.get("match"):
        return resp.get("record") or {}
    return None

# ---------- Smart checklist + Summary (baseline) ----------
def build_smart_checklist(cat, sub, answers, base_list):
    A = {q.lower(): a for q, a in (answers or {}).items()}
    smart = list(base_list or [])
    def add(x):
        if x not in smart: smart.append(x)

    # Common enrichments
    if any("refusal" in q and A[q] == "Yes" for q in A): add("Previous refusal letters / decision notices")
    if any("children" in q and A[q] == "Yes" for q in A): add("Children’s birth certificates & custody/consent")
    if any("english" in q and A[q] == "Yes" for q in A): add("English language certificate (full score sheet)")
    if any("tb" in q and A[q] == "Yes" for q in A): add("TB test certificate")
    if any("accommodation" in q and A[q] == "Yes" for q in A): add("Accommodation inspection report (if available)")
    if any("funds" in q and A[q] == "Yes" for q in A): add("Bank statements (maintained 28 days)")

    key = f"{(cat or '').lower()}|{(sub or '').lower()}"
    if "family immigration|spouse/partner visa" in key:
        add("6 months payslips & bank statements (or self-employment tax returns)")
        add("Relationship evidence over time (photos/travel/logs)")
    if "work immigration|skilled worker visa" in key:
        add("Signed offer/contract")
        add("Sponsor licence number (on CoS)")
    if "study immigration|student visa" in key:
        add("CAS statement & tuition fee receipt")
    if "visit immigration|standard visitor visa" in key:
        add("Employer leave letter and strong home-ties evidence")

    return smart

RED_FLAGS = ["refusal","overstay","breach","criminal","human trafficking","modern slavery","appeal","deport"]
def extract_red_flags(texts):
    flags=set()
    for t in texts or []:
        low=t.lower()
        for k in RED_FLAGS:
            if k in low: flags.add(k)
    return sorted(flags)

def send_summary_email(s):
    name   = s["info"].get("Name","")
    email  = s["info"].get("Email","")
    phone  = s["info"].get("Phone","")
    dob    = s["info"].get("DOB","")
    urgency= s["info"].get("Urgency","")
    cat    = s.get("cat","")
    sub    = s.get("sub","")
    answers= s.get("ans",{})
    docs   = s.get("docs",[])

    red = extract_red_flags(list(answers.keys()))
    doc_lines = "\n".join([f"- {d.get('name')}  {d.get('url','')}" for d in docs]) or "(none yet)"

    body = (
        f"New WhatsApp intake\n\n"
        f"Case: {s['case']}\n"
        f"Type: {cat} → {sub}\n"
        f"Urgency: {urgency}\n"
        f"Client: {name}\nEmail: {email}\nPhone: {phone}\nDOB: {dob}\n\n"
        f"Answers:\n" + "\n".join([f"- {q}: {a}" for q,a in answers.items()]) + "\n\n"
        f"Red flags: {', '.join(red) if red else '(none)'}\n\n"
        f"Uploaded docs:\n{doc_lines}\n"
    )
    call_apps_script({"action":"send_email","to":ADMIN_EMAIL,"subject":f"[Intake] {sub} ({urgency}) — {name}","body":body}, timeout=20)

def calendly_link(s):
    if not CALENDLY_URL: return ""
    params = []
    n=s["info"].get("Name",""); e=s["info"].get("Email","")
    params.append(f"name={requests.utils.quote(n)}")
    params.append(f"email={requests.utils.quote(e)}")
    params.append(f"utm_campaign={requests.utils.quote(s.get('sub','Consultation'))}")
    params.append("utm_source=whatsapp")
    return CALENDLY_URL + "?" + "&".join(params)

def google_calendar_link(s):
    base = "https://calendar.google.com/calendar/render"
    text = f"Immigration consultation — {s.get('sub','')}"
    details = f"Case: {s['case']}\nClient: {s['info'].get('Name','')}\nPhone: {s['info'].get('Phone','')}\n"
    return f"{base}?action=TEMPLATE&text={requests.utils.quote(text)}&details={requests.utils.quote(details)}&ctz={CAL_DEFAULT_TZ}"

# ---------- Append intake to Google Sheet ----------
def append_intake_row(s):
    try:
        values = [
            s.get('case',''),
            s['info'].get('Name',''),
            s['info'].get('Email',''),
            s['info'].get('Phone',''),
            s.get('cat',''),
            s.get('sub',''),
            s['info'].get('Urgency','Normal'),
            s['info'].get('DOB',''),
            json.dumps(s.get('ans',{}), ensure_ascii=False),
            datetime.utcnow().isoformat() + "Z"
        ]
        resp = call_apps_script({
            "action": "append_row",
            "spreadsheetId": SHEET_ID,
            "sheet": SHEET_TAB,
            "values": values
        }, timeout=20)
        # Fallback alternative action name
        if not isinstance(resp, dict) or resp.get("status") not in ("ok","success"):
            call_apps_script({
                "action": "append_intake",
                "spreadsheetId": SHEET_ID,
                "sheet": SHEET_TAB,
                "record": {
                    "caseId": values[0],
                    "name": values[1],
                    "email": values[2],
                    "phone": values[3],
                    "category": values[4],
                    "subservice": values[5],
                    "urgency": values[6],
                    "dob": values[7],
                    "answers": s.get('ans',{}),
                    "createdAt": values[9]
                }
            }, timeout=20)
    except Exception as e:
        print("Sheet append error:", e)

# ---------- Webhook ----------
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        return 'Forbidden', 403
    data = request.get_json(force=True)
    print(f"Incoming webhook data: {data}")
    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            value = change.get('value', {})
            for msg in value.get('messages', []):
                uid = msg.get('from')

                # Capture media uploads at ANY time
                if msg.get("type") in {"document", "image", "audio", "video"}:
                    try:
                        handle_media_anytime(uid, msg)
                    except Exception as e:
                        print("media handling error:", e)

                text = msg.get('text', {}).get('body') if 'text' in msg else None
                itype = iid = ititle = None
                if 'interactive' in msg:
                    inter = msg['interactive']
                    if 'button_reply' in inter:
                        itype, iid, ititle = 'btn', inter['button_reply']['id'], inter['button_reply']['title']
                    elif 'list_reply' in inter:
                        itype, iid, ititle = 'list', inter['list_reply']['id'], inter['list_reply']['title']
                handle(uid, text, itype, iid, ititle)
    return jsonify(status='ok'), 200

def show_faqs(uid, s):
    cat, sub = s['cat'], s['sub']
    faqs = SERVICES[cat]['subservices'][sub]['faqs']
    rows = [(f'faq_{i}', f['q'], '') for i, f in enumerate(faqs)]
    rows.append(('done_faq', 'Done with FAQs', ''))
    # use safe list with fallback
    send_list_safe(uid, T['faq_header'].format(srv=sub), T['faq_body'], 'Select FAQ', rows, fallback_tag="faq")

def anything_else(uid, s):
    name = s['info']['Name']
    body = T['anything_else'].format(name=name)
    opts = [('yes', 'Yes'), ('no', 'No')]
    send_buttons(uid, body, opts)

def handle(uid, text, itype, iid, ititle):
    if uid not in sessions:
        reset(uid)
    s = sessions[uid]
    if text and text.lower() in {'hi', 'menu', 'restart', 'start'}:
        reset(uid)
    state = s['state']
    if text and text.lower() == 'back':
        if state in {'sub', 'elig'}:
            s['state'] = 'cat'
        elif state.startswith('info_'):
            s['state'] = 'elig'
            s['q_idx'] = 0
        elif state == 'faq':
            s['state'] = 'cat'
        elif state == 'anything':
            s['state'] = 'faq'
        elif state == 'llm':
            s['state'] = 'anything'
        handle(uid, None, None, None, None)
        return

    # ----- Global intercept: booking reply buttons (fallback path) -----
    if itype == 'btn' and iid in {'book_cal', 'add_cal'}:
        links = sessions.get(uid, {}).get("_book", {})
        if iid == 'book_cal' and links.get("cal"):
            send_text(uid, f"🔗 Book on Calendly: {links['cal']}")
            return
        if iid == 'add_cal' and links.get("gcal"):
            send_text(uid, f"🗓 Add to Calendar: {links['gcal']}")
            return
        send_text(uid, "Link not ready yet. Please try again.")
        return

    # ----- Category -----
    if state == 'cat':
        # Numeric / name fallback mapping
        if itype is None and text:
            fb = sessions.get(uid, {}).get("_fallback", {}).get("cat")
            if fb and fb.get("mode") == "numbered":
                if text.strip().isdigit():
                    idx = int(text.strip()) - 1
                    items = fb["rows"]
                    if 0 <= idx < len(items):
                        chosen_id = items[idx][0]
                        itype, iid = 'list', chosen_id
                else:
                    for _id, _title, _ in fb["rows"]:
                        if text.strip().lower() in _title.lower():
                            itype, iid = 'list', _id
                            break

        if not itype:
            send_text(uid, T['welcome'])
            rows = [(f'cat_{i}', f'{EMOJI.get(c, "📂")} {c}', '') for i, c in enumerate(SERVICES.keys(), 1)]
            send_list_safe(uid, T['select_category'], T['choose_category'], 'Choose', rows, fallback_tag="cat")
            return

        if itype == 'list' and iid.startswith('cat_'):
            cat_idx = int(iid.split('_')[1]) - 1
            cats = list(SERVICES.keys())
            s['cat'] = cats[cat_idx]
            s['state'] = 'sub'
            subs = SERVICES[s['cat']]['subservices']
            rows = [(f'sub_{i}', ss, '') for i, ss in enumerate(subs.keys(), 1)]
            send_list_safe(uid, T['select_sub'], T['choose_sub'].format(cat=s['cat']), 'Choose', rows, fallback_tag="sub")
            return
        send_text(uid, T['invalid'])
        return

    # ----- Subservice -----
    if state == 'sub':
        # Numeric / name fallback handling
        if itype is None and text:
            fb = sessions.get(uid, {}).get("_fallback", {}).get("sub")
            if fb and fb.get("mode") == "numbered":
                if text.strip().isdigit():
                    idx = int(text.strip()) - 1
                    items = fb["rows"]
                    if 0 <= idx < len(items):
                        chosen_id = items[idx][0]
                        itype, iid = 'list', chosen_id
                else:
                    for _id, _title, _ in fb["rows"]:
                        if text.strip().lower() in _title.lower():
                            itype, iid = 'list', _id
                            break

        cat = s['cat']
        if itype == 'list' and iid.startswith('sub_'):
            sub_idx = int(iid.split('_')[1]) - 1
            subs = list(SERVICES[cat]['subservices'].keys())
            s['sub'] = subs[sub_idx]
            s['state'] = 'elig'
            s['q_idx'] = 0
            s['ans'] = {}
            q = SERVICES[cat]['subservices'][s['sub']]['questions'][0]
            total_q = len(SERVICES[cat]['subservices'][s['sub']]['questions'])
            opts = [('yes', 'Yes ✅'), ('no', 'No ❌'), ('dont', "Don't know ❓")]
            send_text(uid, T['elig_intro'].format(srv=s['sub']))
            send_buttons(uid, T['elig_progress'].format(curr=1, total=total_q) + q, opts)
            return
        send_text(uid, T['invalid'])
        return

    # ----- Eligibility Q&A -----
    if state == 'elig':
        cat, sub = s['cat'], s['sub']
        idx = s['q_idx']
        total_q = len(SERVICES[cat]['subservices'][sub]['questions'])
        if itype == 'btn':
            ans = {'yes': 'Yes', 'no': 'No', 'dont': "Don't know"}.get(iid, ititle)
            qtxt = SERVICES[cat]['subservices'][sub]['questions'][idx]
            s['ans'][qtxt] = ans
            if ans == 'Yes':
                s['score'] += 1
            if 'refusal' in qtxt.lower() and ans == 'Yes':
                s['complex'] = True
            s['q_idx'] += 1
            if s['q_idx'] < total_q:
                nq = SERVICES[cat]['subservices'][sub]['questions'][s['q_idx']]
                opts = [('yes', 'Yes ✅'), ('no', 'No ❌'), ('dont', "Don't know ❓")]
                send_buttons(uid, T['elig_progress'].format(curr=s['q_idx']+1, total=total_q) + nq, opts)
            else:
                s['state'] = 'info_name'
                send_text(uid, T['ask_name'])
            return
        send_text(uid, T['invalid'])
        return

    # ----- Info capture -----
    if state.startswith('info_'):
        fld = state.split('_')[1]
        if text is None and itype is None:
            return

        if fld == 'name':
            s['info']['Name'] = (text or "").strip()
            s['state'] = 'info_dob'
            send_text(uid, "🎂 *Enter your date of birth* (DD/MM/YYYY):")
            return

        if fld == 'dob':
            dob = parse_dob(text)
            if not dob:
                send_text(uid, "Please use DD/MM/YYYY (e.g., 05/09/1994).")
                return
            s['info']['DOB'] = dob
            # Duplicate check
            dup = check_duplicate_in_sheet(s['info'].get('Name', ''), dob)
            if dup:
                s['state'] = 'dup_confirm'
                send_buttons(uid,
                    f"🔎 Similar record found:\n• *Name:* {dup.get('Name','')}\n• *DOB:* {dup.get('DOB','')}\n• *Case ID:* {dup.get('CaseID','')}\n\nContinue anyway?",
                    [('cont','Continue'), ('stop','Stop')]
                )
            else:
                s['state'] = 'info_email'
                send_text(uid, T['ask_email'])
            return

        if fld == 'email':
            if not re.match(r"[^@]+@[^@]+\.[^@]+", text or ""):
                send_text(uid, T['bad_email'])
                return
            s['info']['Email'] = text.strip()
            s['state'] = 'info_phone'
            send_text(uid, T['ask_phone'])
            return

        if fld == 'phone':
            s['info']['Phone'] = text.strip()
            s['state'] = 'info_urgency'
            opts = [('urgent', 'Urgent'), ('normal', 'Normal')]
            send_buttons(uid, T['ask_urgency'], opts)
            return

        if fld == 'urgency' and itype == 'btn':
            s['info']['Urgency'] = ititle

            # Build human-readable notes from Q&A
            qa = s.get('ans', {}) or {}
            notes_lines = [f"{q}: {a}" for q, a in qa.items()]
            notes = "\n".join(notes_lines).strip()

            # Register ONCE
            if not s.get('registered'):
                reg_payload = {
                    "action": "register",
                    "name": s["info"].get("Name",""),
                    "email": s["info"].get("Email",""),
                    "phone": s["info"].get("Phone",""),
                    "phoneNumber": uid,
                    "visaRoute": s.get("sub",""),
                    "urgency": s["info"].get("Urgency","Normal"),
                    "evidenceChecklist": SERVICES[s['cat']]['subservices'][s['sub']]['checklist'],
                    "notes": "\n".join([f"{q}: {a}" for q,a in (s.get('ans') or {}).items()]).strip()
                }
                result = call_apps_script(reg_payload)
                ok = False
                if isinstance(result, dict):
                    status = (result.get("status") or "").lower()
                    ok = status in {"success", "ok"} or bool(result.get("caseId"))

                if ok:
                    s["registered"] = True
                    s["case"] = result.get("caseId", s["case"])
                    intake_link = result.get("intakeFormLink","")
                    upload_link = result.get("uploadDocsLink","")
                    drive_link  = result.get("driveFolderLink","")
                    msg = (
                        "✅ *Your case has been registered.*\n\n"
                        f"*Case ID:* {s['case']}\n\n"
                        "🧭 *Next steps*\n"
                        f"1) Intake form: {intake_link}\n"
                        f"2) Upload documents: {upload_link}\n"
                        f"3) Case folder (internal): {drive_link}"
                    )
                    send_text(uid, msg)
                else:
                    err = result.get("message") if isinstance(result, dict) else "unknown"
                    send_text(uid, f"⚠️ We couldn’t auto-register your case. ({err}) We’ll follow up by email.")

            # Send personalized checklist once
            cat, sub = s['cat'], s['sub']
            base = SERVICES[cat]['subservices'][sub]['checklist']
            smart = build_smart_checklist(cat, sub, s.get('ans', {}), base)
            send_text(uid, T['doclist'].format(srv=sub, list="\n".join([f"• {c}" for c in base])))
            if smart:
                send_text(uid, "🧠 *Smart Checklist*\n" + "\n".join([f"• {x}" for x in smart]))

            # Email + append sheet just once (optional, but keep after registration)
            try: send_summary_email(s)
            except Exception as e: print("summary email error:", e)
            try: append_intake_row(s)
            except Exception as e: print("append_intake_row error:", e)

            # Booking buttons (template first; reply-button fallback)
            try: send_booking_cta(uid, s)
            except Exception as e: print("booking cta error:", e)

            name = s['info']['Name']
            send_text(uid, f"Hello {name}, {T['email_docs']}")
            s['state'] = 'faq'
            show_faqs(uid, s)
            return


    # ----- Duplicate confirm -----
    if state == 'dup_confirm':
        if itype == 'btn' and iid in {'cont','stop'}:
            if iid == 'stop':
                send_text(uid, "Okay, stopping here to avoid a duplicate. Reply *start* anytime to begin again.")
                sessions.pop(uid, None)
                return
            s['state'] = 'info_email'
            send_text(uid, T['ask_email'])
            return
        send_text(uid, "Please choose *Continue* or *Stop*.")
        return

    # ----- FAQs / LLM -----
    if state == 'faq':
        # numeric/name fallback for FAQs
        if itype is None and text:
            fb = sessions.get(uid, {}).get("_fallback", {}).get("faq")
            if fb and fb.get("mode") == "numbered":
                if text.strip().isdigit():
                    idx = int(text.strip()) - 1
                    items = fb["rows"]
                    if 0 <= idx < len(items):
                        chosen_id = items[idx][0]
                        itype, iid = 'list', chosen_id
                else:
                    for _id, _title, _ in fb["rows"]:
                        if text.strip().lower() in _title.lower():
                            itype, iid = 'list', _id
                            break

        if itype == 'list':
            if iid.startswith('faq_'):
                faq_idx = int(iid.split('_')[1])
                cat, sub = s['cat'], s['sub']
                faq = SERVICES[cat]['subservices'][sub]['faqs'][faq_idx]
                send_text(uid, T['faq_answer'].format(q=faq['q'], a=faq['a']))
                s['state'] = 'anything'
                anything_else(uid, s)
                return
            if iid == 'done_faq':
                s['state'] = 'anything'
                anything_else(uid, s)
                return
        if text:
            ctx = f"{s['cat']} – {s['sub']}"
            ans = ask_llm(text, ctx)
            send_text(uid, ans)
            s['state'] = 'anything'
            anything_else(uid, s)
            return
        send_text(uid, T['invalid'])
        return

    # ----- Anything else / end -----
    if state == 'anything':
        if itype == 'btn':
            if iid == 'yes':
                s['state'] = 'llm'
                name = s['info']['Name']
                srv = s['sub']
                send_text(uid, T['ask_question'].format(srv=srv, name=name))
                return
            if iid == 'no':
                name = s['info']['Name']
                send_text(uid, T['thank_you'].format(name=name))
                opts = [('start_again', T['start_new'])]
                send_buttons(uid, "", opts)
                del sessions[uid]
                return
        elif text:
            if text.lower() == 'yes':
                s['state'] = 'llm'
                name = s['info']['Name']
                srv = s['sub']
                send_text(uid, T['ask_question'].format(srv=srv, name=name))
                return
            elif text.lower() == 'no':
                name = s['info']['Name']
                send_text(uid, T['thank_you'].format(name=name))
                opts = [('start_again', T['start_new'])]
                send_buttons(uid, "", opts)
                del sessions[uid]
                return
        send_text(uid, T['invalid'])
        return

    if state == 'llm':
        if text:
            ctx = f"{s['cat']} – {s['sub']}"
            ans = ask_llm(text, ctx)
            send_text(uid, ans)
            s['state'] = 'anything'
            anything_else(uid, s)
            return
        send_text(uid, T['invalid'])
        return

    if itype == 'btn' and iid == 'start_again':
        reset(uid)
        handle(uid, None, None, None, None)
        return

    send_text(uid, T['fallback'])


# =========================
# PATCH: Rich booking (Option C) and helpers
# =========================

# -- Template name/lang & URL bases (for URL buttons in templates) --
WA_TEMPLATE_BOOKING = os.getenv("WA_TEMPLATE_BOOKING", "immigration_booking_v1")
WA_TEMPLATE_LANG    = os.getenv("WA_TEMPLATE_LANG", "en_GB")
# WhatsApp requires button URLs to share fixed bases. Configure the bases below:
TEMPLATE_URL0_BASE  = os.getenv("TEMPLATE_URL0_BASE", "https://calendly.com/yourteam/")
TEMPLATE_URL1_BASE  = os.getenv("TEMPLATE_URL1_BASE", "https://go.yoursite.xyz/")  # your short domain for calendar link

def _shortener(long_url: str) -> str:
    """Use Apps Script to shorten links; fall back gracefully."""
    # Try `shorten_url` contract
    try:
        r = call_apps_script({"action": "shorten_url", "url": long_url}, timeout=10)
        if isinstance(r, dict) and r.get("status") == "ok" and r.get("short"):
            return r["short"]
    except Exception as e:
        print("shorten_url error:", e)
    # Try alternative `shorten` contract
    try:
        r = call_apps_script({"action": "shorten", "url": long_url}, timeout=10)
        if isinstance(r, dict) and (r.get("ok") or r.get("status") == "ok"):
            return r.get("shortUrl") or r.get("short_url") or long_url
    except Exception as e:
        print("shorten (alt) error:", e)
    return long_url

# Override google_calendar_link to return a shortened link (useful even in fallbacks)
def google_calendar_link(s):  # redefines earlier function intentionally
    base = "https://calendar.google.com/calendar/render"
    text = f"Immigration consultation — {s.get('sub','')}"
    details = f"Case: {s['case']}\nClient: {s['info'].get('Name','')}\nPhone: {s['info'].get('Phone','')}\n"
    long = f"{base}?action=TEMPLATE&text={requests.utils.quote(text)}&details={requests.utils.quote(details)}&ctz={CAL_DEFAULT_TZ}"
    return _shortener(long)

def _send_template_booking(to: str, calendly_url: str, gcal_short_url: str) -> bool:
    """Send the WhatsApp template with two URL buttons. Returns True if sent."""
    if not (WA_TEMPLATE_BOOKING and WA_TEMPLATE_LANG and calendly_url and gcal_short_url):
        return False
    # Both URLs must start with the pre-approved bases
    if not calendly_url.startswith(TEMPLATE_URL0_BASE): return False
    if not gcal_short_url.startswith(TEMPLATE_URL1_BASE): return False

    # Calculate URL suffixes required by WhatsApp templates
    suffix0 = calendly_url[len(TEMPLATE_URL0_BASE):]
    suffix1 = gcal_short_url[len(TEMPLATE_URL1_BASE):]

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": WA_TEMPLATE_BOOKING,
            "language": {"code": WA_TEMPLATE_LANG},
            "components": [
                {"type": "button", "sub_type": "url", "index": "0",
                 "parameters": [{"type": "text", "text": suffix0}]},
                {"type": "button", "sub_type": "url", "index": "1",
                 "parameters": [{"type": "text", "text": suffix1}]}
            ]
        }
    }
    try:
        r = requests.post(WA_URL, headers=HDRS, json=payload, timeout=12)
        if r.status_code >= 300:
            print("Template send failed:", r.text)
        return r.status_code < 300
    except Exception as e:
        print("Template send exception:", e)
        return False

def send_booking_cta(uid: str, s: dict):
    """
    Primary booking UX: try template URL buttons; otherwise show reply buttons.
    No raw long URLs are sent in the initial message.
    """
    cal = calendly_link(s)
    gcal = google_calendar_link(s)  # already shortened

    # Stash for fallback button clicks
    sessions.setdefault(uid, {}).setdefault("_book", {})
    sessions[uid]["_book"]["cal"]  = cal
    sessions[uid]["_book"]["gcal"] = gcal

    # Try template buttons first (best UX; hides links entirely)
    sent = False
    try:
        sent = _send_template_booking(uid, cal, gcal)
    except Exception as e:
        print("send_booking_cta template error:", e)

    # If template not available, use reply buttons; links are only revealed on tap
    if not sent:
        send_buttons(uid, "Quick actions:", [
            ("book_cal", "📅 Book on Calendly"),
            ("add_cal",  "🗓 Add to Calendar")
        ])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
