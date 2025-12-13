from fpdf import FPDF

# Create instance of FPDF class
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", 'B', 16)

# Title
pdf.cell(0, 10, "Dummy Persons List", ln=True, align="C")
pdf.ln(10)

# Dummy persons data
persons = [
    {
        "Name": "Ramesh Sharma",
        "Phone": "+977 976-1445644",
        "Email": "ramesh.sharma@example.com",
        "Address": "Kathmandu, Nepal"
    },
    {
        "Name": "Suresh Adhikari",
        "Phone": "+977 986-1369691",
        "Email": "suresh.adhikari@example.com",
        "Address": "Lalitpur, Nepal"
    }
]

# Add persons to PDF
for i, person in enumerate(persons, start=1):
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Person {i}", ln=True)
    pdf.set_font("Arial", '', 12)
    for key, value in person.items():
        pdf.cell(0, 8, f"{key}: {value}", ln=True)
    pdf.ln(5)

# Save PDF
pdf_file_path = "contact.pdf"
pdf.output(pdf_file_path)
pdf_file_path
