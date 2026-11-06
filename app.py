import streamlit as st
import json
import re
import os
from datetime import datetime
import pandas as pd

# ================= 1. OOP: Voter - Uses NIN =================
class Voter:
    def __init__(self, name, nin, phone, dob):
        self.name = name
        self.nin = nin
        self.phone = phone
        self.dob = dob
        self.has_voted = False

    def to_dict(self):
        return {
            "name": self.name,
            "nin": self.nin,
            "phone": self.phone,
            "dob": self.dob,
            "has_voted": self.has_voted
        }

# ================= 2. OOP: Candidate =================
class Candidate:
    def __init__(self, name, party, position):
        self.name = name
        self.party = party
        self.position = position
        self.votes = 0

    def to_dict(self):
        return {"name": self.name, "party": self.party, "position": self.position, "votes": self.votes}

# ================= 3. OOP: ElectionStore =================
class ElectionStore:
    def __init__(self, filename="election_data.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            default = {
                "voters": [
                    # YOUR VOTER ALREADY REGISTERED
                    {"name": "Nathaniel Bitrus Kaigama", "nin": "45469410619", "phone": "08000000000", "dob": "2000-01-01", "has_voted": False}
                ],
                "candidates": [
                    {"name": "Nathaniel Bitrus Kaigama", "party": "PDP", "position": "President", "votes": 0},
                    {"name": "Amina Bello", "party": "APC", "position": "President", "votes": 0},
                    {"name": "Musa Ibrahim", "party": "LP", "position": "President", "votes": 0},
                    {"name": "Fatima Yusuf", "party": "NNPP", "position": "Governor", "votes": 0},
                    {"name": "Emeka Eze", "party": "APC", "position": "Governor", "votes": 0},
                ],
                "votes_log": []
            }
            with open(self.filename, "w") as f:
                json.dump(default, f, indent=2)

    def load(self):
        try:
            with open(self.filename, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"voters": [], "candidates": [], "votes_log": []}

    def save(self, data):
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)

    def register_voter(self, voter):
        data = self.load()
        for v in data["voters"]:
            if v["nin"] == voter.nin:
                raise ValueError(f"NIN {voter.nin} is already registered!")
        data["voters"].append(voter.to_dict())
        self.save(data)

    def cast_vote(self, nin, candidate_name, position):
        data = self.load()
        voter = None
        for v in data["voters"]:
            if v["nin"] == nin:
                voter = v
                break
        if not voter:
            raise ValueError("NIN not found! Register first with your NIN.")
        if voter["has_voted"]:
            raise ValueError("This NIN has ALREADY voted! One NIN, One Vote.")
        found = False
        for c in data["candidates"]:
            if c["name"] == candidate_name and c["position"] == position:
                c["votes"] += 1
                found = True
                break
        if not found:
            raise ValueError("Candidate not found!")
        voter["has_voted"] = True
        data["votes_log"].append({
            "nin": nin,
            "candidate": candidate_name,
            "position": position,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save(data)

# ================= 4. OOP: ElectionValidator - REGEX =================
class ElectionValidator:
    def validate_nin(self, nin):
        nin = nin.strip()
        if not re.match(r"^\d{11}$", nin):
            raise ValueError("Invalid NIN! NIN must be exactly 11 numbers. Example: 45469410619")
        return nin

    def validate_name(self, name):
        if not re.match(r"^[A-Za-z\s]{3,40}$", name.strip()):
            raise ValueError("Invalid name! Use only letters.")
        return name.strip().title()

    def validate_phone(self, phone):
        if not re.match(r"^(\+234|0)[789]\d{9}$", phone.strip()):
            raise ValueError("Invalid phone! Use e.g. 08031234567")
        return phone.strip()

    def validate_dob(self, dob):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob.strip()):
            raise ValueError("Invalid DOB! Use YYYY-MM-DD e.g. 2000-05-12")
        return dob.strip()

# ================= STREAMLIT UI =================
st.set_page_config(page_title="NIN Election Voting App", page_icon="🗳️")
st.title("🗳️ Nigeria Election Voting App")
st.write("Vote with your NIN. One NIN = One Vote.")

store = ElectionStore()
validator = ElectionValidator()

menu = st.sidebar.selectbox("Menu", ["Vote", "Register Voter", "Results", "Admin"])

# --- REGISTER ---
if menu == "Register Voter":
    st.header("📝 Register With NIN")
    nin = st.text_input("1. Enter Your NIN (11 digits) *", placeholder="e.g. 45469410619", max_chars=11)
    name = st.text_input("2. Full Name", placeholder="e.g. Nathaniel Bitrus Kaigama")
    phone = st.text_input("3. Phone Number", placeholder="e.g. 08031234567")
    dob = st.text_input("4. Date of Birth (YYYY-MM-DD)", placeholder="e.g. 2000-05-12")
    if st.button("Register With NIN"):
        try:
            clean_nin = validator.validate_nin(nin)
            clean_name = validator.validate_name(name)
            clean_phone = validator.validate_phone(phone)
            clean_dob = validator.validate_dob(dob)
            store.register_voter(Voter(clean_name, clean_nin, clean_phone, clean_dob))
            st.success(f"✅ Registered! Name: {clean_name}, NIN: {clean_nin}")
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Error: {e}")

# --- VOTE ---
elif menu == "Vote":
    st.header("✅ Vote With Your NIN")
    st.info("You are already registered as Nathaniel Bitrus Kaigama. Use your NIN to vote.")
    nin = st.text_input("Enter Your NIN to Vote (11 digits)", value="45469410619", max_chars=11)
    position = st.selectbox("Choose Position", ["President", "Governor"])
    data = store.load()
    candidates = [c for c in data["candidates"] if c["position"] == position]
    names = [f"{c['name']} - {c['party']}" for c in candidates]
    choice = st.selectbox("Choose Candidate", names)
    if st.button("Submit Vote 🗳️"):
        try:
            clean_nin = validator.validate_nin(nin)
            candidate_name = choice.split(" - ")[0]
            store.cast_vote(clean_nin, candidate_name, position)
            st.success(f"🎉 Vote counted for {candidate_name}!")
            st.success(f"NIN {clean_nin} has now voted.")
            st.balloons()
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Error: {e}")

# --- RESULTS ---
elif menu == "Results":
    st.header("📊 Live Results")
    data = store.load()
    st.metric("Registered Voters (by NIN)", len(data["voters"]))
    st.metric("Total Votes Cast", len(data["votes_log"]))
    if data["candidates"]:
        df = pd.DataFrame(data["candidates"])
        st.dataframe(df)
        st.subheader("Who is Winning?")
        st.bar_chart(df.set_index("name")["votes"])
        if len(data["votes_log"]) > 0:
            winner = df.loc[df["votes"].idxmax()]
            st.success(f"🏆 Currently Leading: {winner['name']} ({winner['party']}) - {winner['votes']} votes")

# --- ADMIN ---
elif menu == "Admin":
    st.header("🔐 Admin Panel")
    password = st.text_input("Admin Password", type="password")
    if password == "admin123":
        data = store.load()
        st.write("All Voters:")
        st.dataframe(data["voters"])
        st.write("Votes Log:")
        st.dataframe(data["votes_log"])
        if st.button("Reset Election (Delete All)"):
            if os.path.exists("election_data.json"):
                os.remove("election_data.json")
            st.success("Election reset! Refresh page.")
    elif password:
        st.error("Wrong password! Hint: admin123")