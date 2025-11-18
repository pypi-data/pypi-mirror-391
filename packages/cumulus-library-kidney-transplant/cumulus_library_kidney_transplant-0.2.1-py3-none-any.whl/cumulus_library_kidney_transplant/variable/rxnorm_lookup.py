from typing import List
from cumulus_library_kidney_transplant.vocab import Vocab

##############################################################################
# Anti-Metabolites
Azathioprine = ['Azathioprine',
                'Imuran',
                'Azasan',
                '6-Mercaptopurine', '6 Mercaptopurine']

Mycophenolate = ['Mycophenolate',
                 'MMF',
                 'CellCept',
                 'Myfortic',
                 'Mycophenolic Acid']

##############################################################################
# CNI Inhibitors
Cyclosporin = ['Cyclosporin', 'Cyclosporine', 'Ciclosporin',
               'Neoral',
               'Sandimmune',
               'Gengraf',
               'Restasis',
               'Cequa']

Tacrolimus = ['Tacrolimus',
              'FK506',
              'Prograf',
              'Protopic',
              'Advagraf',
              'Fujimycin',
              'Envarsus']
##############################################################################
# Corticosteroids

Methylprednisolone = ['Methylprednisolone', 'Medrol', 'Solu-Medrol', 'Depo-Medrol', 'A-Methapred']
Prednisolone = ['Prednisolone', 'Orapred', 'Pediapred', 'Prelone', 'Flo-Pred', 'Millipred', 'Veripred']
Prednisone = ['Prednisone', 'Deltasone', 'Rayos', 'Sterapred', 'Prednicot']

##############################################################################
# Belatacept
# (inhibits T-cell co-stimulation )
Belatacept = ['Belatacept',
              'CTLA-4-Ig','CTLA 4 Ig',
              'LEA29Y',
              'Nulojix']

##############################################################################
# Monoclonal (and polyclonal ATG) antibodies
Alemtuzumab = ['Alemtuzumab', 'Campath', 'Lemtrada', 'LDP-03', 'MabCambath']

ATG = ['ATGAM',
       'Anti-Thymocyte Globulin', 'Anti Thymocyte Globulin',
       'Antithymocyte immunoglobulin',
       'Thymoglobulin', 'lymphocyte immune globulin']

Basiliximab = ['Basiliximab', 'Simulect', 'CHI 621']

Rituximab = ['Rituximab', 'Rituxan',
             'Truxima',
             'Ruxience',
             'IDEC-102',
             'MabThera',
             'Reditux',
             'RTXM 83']

##############################################################################
# MTOR
Everolimus = ['Everolimus',
              'Certican',
              'Zortress',
              'Afinitor',
              'Votubia',
              'RAD001',
              'Torpenz',
              'SDZ-RAD']

Sirolimus = ['Sirolimus',
            'Rapamune', 'Rapamycin',
             'AY-22989', 'AP 21967',
            'Streptomyces hygroscopicus']

##############################################################################
# DRUG LIST

# ANTI_METABOLITE = Azathioprine + Mycophenolate
# CNI = Cyclosporin + Tacrolimus
# MTOR = Everolimus + Sirolimus
# STEROID = Prednisone + Methylprednisolone + Prednisolone
# MAB = Alemtuzumab + Atg + Basiliximab + Rituximab
# IVIG = IVIG + IG

##############################################################################
Cytogam = ['Cytogam',
           'cytomegalovirus%immunoglobulin','cytomegalovirus%immune%globulin',
           'Cytomegalovirus%Intravenous', 'Intravenous%Cytomegalovirus']

IVIG = ['Gammagard','Privigen', 'Gamunex', 'Gammaked', 'Octagam', 'Flebogamma', 'Gammaplex', 'Bivigam', 'Panzyga',
        'Alyglo', 'Asceniv', 'Carimune', 'Yimmugo',
        'Immun%Globulin%Infusion', 'Immun%Globulin%Inject', 'Immun%Globulin%Intravenous',
        'IGG%Infusion', 'IGG%Inject', 'IGG%Intravenous',
        'IGG%intravenous', 'IGG%inject']

IG = ['Hizentra', 'Cuvitru', 'Xembify', 'Hyqvia', 'Cutaquig', 'Gamunex-C',
      'Gamimune N', 'human-klhw',
      'Immun%Globulin%Subcutan', 'IGG%Subcutan']

DRUG_LIST = [Azathioprine, Mycophenolate,
             Cyclosporin, Tacrolimus,
             Everolimus, Sirolimus,
             Prednisone, Prednisolone, Methylprednisolone,
             Alemtuzumab, ATG, Basiliximab, Rituximab,
             Belatacept,
             Cytogam, IVIG, IG]

###############################################################################
#
# Simple helper functions
#
###############################################################################

def str_like(keywords: List[str]) -> str:
    where = list()
    for token in keywords:
        where.append(f"lower(str) like lower('%{token}%')")
    return '\nOR '.join(where)

def select_code_display(keywords, sab='RXNORM') -> str:
    partition  = 'row_number() over (partition by code order by length(str), str) as rn'
    source = 'umls.MRCONSO_drugs'
    rxnorm = Vocab.RXNORM
    where = f" SAB='{sab}' and \n ( {str_like(keywords)})"
    select = f"SELECT '{rxnorm}' as system, code, display FROM ranked WHERE rn = 1 order by code"
    return f"with ranked AS ( select code, str as display, {partition} from {source} where {where}) \n {select};\n"

###############################################################################
#
# Build a SQL file for executing against UMLS/Athena
#
###############################################################################
if __name__ == "__main__":
    for drug in DRUG_LIST:
        print('####################################')
        print(drug)
        sql = select_code_display(drug)
        print(sql)
