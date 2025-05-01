CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Date date,
    Caregiver varchar(255) REFERENCES Caregivers(Username),
    PRIMARY KEY (Date, Caregiver)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (

    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)

);

CREATE TABLE Appointments (

    Appointment_id int NOT NULL IDENTITY(1, 1),
    Date date NOT NULL,
    Vaccine varchar(255) REFERENCES Vaccines(Name) NOT NULL,
    Caregiver varchar(255) REFERENCES Caregivers(Username) NOT NULL,
    Patient varchar(255) REFERENCES Patients(Username) NOT NULL,
    PRIMARY KEY (Appointment_id)

);

