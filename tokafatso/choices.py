
RESULT_VALIDATION_STATUS = (
    ('P','Preliminary'),
    ('F','Final'),
    ('R','Rejected'),
)

RESULT_QUANTIFIER = (
    ('=','='),
    ('>','>'),
    ('>=','>='),
    ('<','<'),
    ('<=','<='),                                                            
)

ABS_CALC = (
    ('absolute', 'Absolute'),
    ('calculated', 'Calculated'),    
    )

UNITS = (
    ('%','%'),
    ('10^3/uL','10^3/uL'),
    ('10^3uL','10^3uL'),
    ('10^6/uL','10^6/uL'),
    ('cells/ul','cells/ul'),
    ('copies/ml','copies/ml'),
    ('fL','fL'),
    ('g/dL','g/dL'),
    ('g/L','g/L'),
    ('mg/L','mg/L'),
    ('mm/H','mm/H'),
    ('mmol/L','mmol/L'),
    ('ng/ml','ng/ml'),
    ('pg','pg'),
    ('ratio','ratio'),
    ('U/L','U/L'),
    ('umol/L','umol/L'),
)

ANC_CLINICS = (
    ('0001', 'Test Clinic - 0001'),
    ('5306', 'Kopong Clinic - 5306'),
    ('5309', 'Metsimotlhabe Clinic - 5309'),
    ('5312', 'Mogoditshane Clinic - 5312'),
    ('5316', 'Nkoyaphiri Clinic - 5316'),
    ('5412', 'Mmopane Health Post - 5412'),
    ('15302', 'Bontleng Clinic - 15302'),
    ('15303', 'Broadhurst 1 Clinic - 15303'),
    ('15304', 'Broadhurst 2 Clinic - 15304'),
    ('15305', 'BTA Clinic - 15305'),
    ('15306', 'Extension 14 Clinic - 15306'),
    ('15307', 'Extension 15 Clinic - 15307'),
    ('15308', 'Old Naledi Clinic - 15308'),
    ('15310', 'Tsholofelo Clinic BH3 - 15310'),
    ('15312', 'Gaborone West Clinic - 15312'),
    ('15314', 'Julia Molefe Clinic Block 9 - 15314'),
    ('15315', 'Phase 2 Clinic - 15315'),
    ('15316', 'Extension 2 Clinic - 15316'),
    ('15325', 'Kgatelopele Clinic Block 8 - 15325'),
    ('17307', 'Tlokweng Clinic - 17307'),
    ('17310', 'Mafitlhakgosi Clinic - 17310'),
)

DRAW_LOCATIONS = (
    ('site', 'On Site'),
    ('external', 'Another Clinic/Hospital'),
)

HAART_STATUS = (
    ('no', 'Not on HAART'),
    ('yes', 'On HAART'),
)


RESULT_VALIDATION_STATUS = (
    ('P','Preliminary'),
    ('F','Final'),
    ('R','Rejected'),
)


REQUISITION_STATUS = (
    ('new', '(New) New requisition'),
    ('prelim', '(Prelim) Preliminary result'),
    ('complete', '(Complete) Valid result'),
    ('sent', '(Sent) SMS Message was sent'),
    ('final','(Final) SMS Message was confirmed'),
    ('multiple_results', '(Error) Multiple result records'),
    ('multiple_validation', '(Error) Multiple validations records'),
    ('mismatched_validation','(Error) Validation record does not match FACS result'),
    ('waiting', '(Waiting) Validation present but no matching FACS result'),
)

POS_NEG_UNKNOWN = (
    ('POS', 'Positive'),
    ('NEG', 'Negative'),
    ('UNKNOWN', 'Unknown'),
)

DATE_ESTIMATED = (
    ('-', 'No'),
    ('D', 'Yes, estimated the Day'),            
    ('MD', 'Yes, estimated Month and Day'),
    ('YMD', 'Yes, estimated Year, Month and Day'),            
)

GENDER = (
    ('M', 'Male'),
    ('F', 'Female'),
)

MESSAGE_TYPE = (
        ('result', 'Result Message'),
        ('status', 'Status Message'),
        ('query' , 'Query Message'),
        ('unauth', 'Unauthorized Message'),
        ('received', 'Received Message')
        )

MESSAGE_DELIVERY_REPORTS = (
        ('1','Delivery success'),
        ('2', 'Delivery failure'),
        ('4', 'Message buffered'),
        ('8', 'Smsc submit'),
        ('16', 'Smsc reject'),
        )
