"""
viva_theory.py
--------------
CBSE Class 12 IP Theory & Viva Questions Module:
Covers:
- Societal Impacts: Cyber Crime, Cyber Safety, Digital Footprints, Phishing, E-Waste Management
- Computer Networks: Types (LAN, MAN, WAN), Topologies (Star, Bus, Ring), Devices (Hub, Switch, Router), Web terms (URL, IP address, DNS)
- Database Concepts: Keys (Primary, Candidate, Alternate, Foreign), DDL vs DML vs TCL
- Pandas & Matplotlib Viva FAQs
"""

THEORY_TOPICS = {
    "1": {
        "title": "Societal Impacts & Cyber Safety",
        "content": """
[1] Cybercrime:
    - Any illegal activity carried out using a computer, network, or the Internet.
    - Examples: Hacking, Phishing, Identity Theft, Cyber Bullying, Ransomware.

[2] Cyber Safety Best Practices:
    - Use strong, unique alphanumeric passwords with special characters.
    - Enable Multi-Factor Authentication (MFA / 2FA).
    - Avoid clicking on suspicious links or downloading attachments from unknown senders.
    - Keep software, operating systems, and antivirus definitions updated.

[3] Digital Footprint:
    - Active: Data you deliberately submit online (emails, social media posts).
    - Passive: Data collected without direct knowledge (browsing history, cookies, IP logs).

[4] E-Waste Management (Electronic Waste):
    - Discarded electronic equipment (old PCs, phones, batteries, circuit boards).
    - Hazardous elements: Lead, Mercury, Cadmium can contaminate soil and groundwater.
    - Solutions: 3 R's (Reduce, Reuse, Recycle), dispose only via authorized e-waste recyclers.
"""
    },
    "2": {
        "title": "Computer Networks Concepts",
        "content": """
[1] Network Types:
    - LAN (Local Area Network)    : Covers small area (Room, Building, School Campus).
    - MAN (Metropolitan Area Net) : Covers a city or town (e.g., Cable TV network).
    - WAN (Wide Area Network)     : Covers country or globe (e.g., The Internet).

[2] Network Topologies:
    - Star Topology : All nodes connected to a central switch/hub. Fault tolerant, easy to maintain.
    - Bus Topology  : All nodes connected to a single central cable (backbone). Inexpensive, but failure in cable stops network.
    - Tree Topology : Hierarchical combination of Star and Bus topologies.

[3] Network Devices:
    - Modem  : Modulator-Demodulator (converts digital signals to analog and vice-versa).
    - Hub    : Broadcasts data to all connected devices (passive, non-intelligent).
    - Switch : Unicasts data to target device using MAC address (intelligent device).
    - Router : Directs data packets across different networks using IP addresses.
    - Gateway: Connects two dissimilar networks working on different protocols.

[4] Web Concepts:
    - URL (Uniform Resource Locator) : Web address (e.g., https://www.cbse.gov.in)
    - IP Address : Unique numerical label assigned to every device on a network.
    - DNS (Domain Name System) : Translates human-friendly domain names to IP addresses.
"""
    },
    "3": {
        "title": "Database Concepts & SQL Keys (DBMS)",
        "content": """
[1] Relational Keys:
    - Primary Key   : Uniquely identifies each record in a table. Cannot be NULL or duplicated.
    - Candidate Key : All attributes/columns that have the ability to uniquely identify a record.
    - Alternate Key : Candidate keys that were NOT chosen as the Primary Key.
    - Foreign Key   : A field that refers to the Primary Key of another table, maintaining Referential Integrity.

[2] SQL Command Categories:
    - DDL (Data Definition Language)   : CREATE, ALTER, DROP (modifies table structure).
    - DML (Data Manipulation Language) : INSERT, SELECT, UPDATE, DELETE (modifies table data).
    - TCL (Transaction Control)        : COMMIT (save), ROLLBACK (undo), SAVEPOINT.

[3] SQL Functions:
    - Aggregate : COUNT(), SUM(), AVG(), MIN(), MAX() (work on multiple rows, return 1 value).
    - String    : CONCAT(), UCASE(), LCASE(), LENGTH(), SUBSTR().
    - Math      : ROUND(), TRUNCATE(), SQRT(), MOD(), POWER().
"""
    },
    "4": {
        "title": "Pandas & Data Visualisation Quick Reference",
        "content": """
[1] Pandas Series vs DataFrame:
    - Series    : 1-Dimensional homogeneous labeled array.
    - DataFrame : 2-Dimensional heterogeneous tabular data structure with labeled axes (rows and columns).

[2] loc[] vs iloc[]:
    - loc[]  : Label-based indexing (e.g., df.loc[0, 'Name'] or df.loc['a':'c']).
    - iloc[] : Integer position-based indexing (e.g., df.iloc[0, 1]).

[3] Matplotlib Pyplot Functions:
    - Line chart : plt.plot(x, y)
    - Bar chart  : plt.bar(x, y) or plt.barh(x, y)
    - Histogram  : plt.hist(data, bins)
    - Scatter    : plt.scatter(x, y)
    - Pie chart  : plt.pie(data, labels, autopct='%1.1f%%')
    - Boxplot    : plt.boxplot(data)
"""
    }
}

def show_viva_menu():
    while True:
        print("\n" + "=" * 65)
        print(" CBSE CLASS 12 IP VIVA & THEORY QUICK REVISION ".center(65, "="))
        print("=" * 65)
        print("1. 🛡️  Cyber Safety, Cybercrime & E-Waste Management")
        print("2. 🌐 Computer Networks, Topologies & Devices")
        print("3. 🗄️  Database Concepts, Keys (Primary/Foreign) & SQL")
        print("4. 🐼 Pandas Series, DataFrame & Matplotlib Summary")
        print("5. ↩️  Back to Main Menu")

        ch = input("\nSelect Topic (1-5): ").strip()
        if ch in THEORY_TOPICS:
            t = THEORY_TOPICS[ch]
            print("\n" + "-" * 65)
            print(f" {t['title']} ".center(65, "-"))
            print("-" * 65)
            print(t["content"])
            input("\n[Press Enter to return to Theory Menu...]")
        elif ch == "5":
            break
        else:
            print("[!] Invalid choice. Please choose 1-5.")
