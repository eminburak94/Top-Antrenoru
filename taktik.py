"""Open-play instructions, position-specific roles and tactical behaviour."""
from mevkiler import fit_level


OPTIONS={
    'press':('Pres','Press',('Düşük','Normal','Yüksek'),('Low','Normal','High')),
    'tempo':('Tempo','Tempo',('Düşük','Normal','Yüksek'),('Low','Normal','High')),
    'width':('Genişlik','Width',('Dar','Dengeli','Geniş'),('Narrow','Balanced','Wide')),
    'line':('Savunma çizgisi','Defensive line',('Derin','Dengeli','Önde'),('Deep','Balanced','High')),
    'passing':('Pas uzunluğu','Passing length',('Kısa','Karma','Doğrudan'),('Short','Mixed','Direct')),
    'flank':('Hücum yönü','Attack focus',('Sol','Karma','Sağ'),('Left','Mixed','Right')),
    'counter':('Geçiş oyunu','Transition',('Topu tut','Dengeli','Kontraatak'),('Retain','Balanced','Counter')),
    'overlap':('Bek desteği','Fullback support',('Geride kal','Dengeli','İleri çık'),('Hold','Balanced','Advance')),
}
EXTRA=('line','passing','flank','counter','overlap')
FULLBACKS=frozenset(('RB','LB','RWB','LWB'))
CENTRE_BACKS=frozenset(('CB','SW'))
ROLES={
    'defensive_back':('Savunmacı bek','Defensive fullback','Çizgiyi geriden korur.','Holds the flank from deeper positions.','Positioning'),
    'wingback':('Hücumcu bek','Attacking fullback','Top sizdeyken bindirir, arkasında alan bırakabilir.','Overlaps in possession and can leave space behind.','Pace'),
    'stopper':('Klasik stoper','Centre-back','Merkezi ve savunma çizgisini korur.','Holds the centre and protects the defensive line.','Marking'),
    'ball_playing':('Pasör stoper','Ball-playing centre-back','Geriden pas bağlantısı kurar.','Offers a passing outlet from the back.','Passing'),
    'ball_winner':('Top kazanan orta saha','Ball-winning midfielder','Rakipte top varken baskıya yaklaşır.','Steps towards the ball out of possession.','Tackling'),
    'playmaker':('Oyun kurucu','Playmaker','Pas almak için topa yaklaşır ve pas trafiğine girer.','Drops towards the ball and becomes a passing outlet.','Vision'),
    'box_to_box':('İki yönlü orta saha','Box-to-box midfielder','Hücumda ileri koşar, savunmada geri döner.','Runs forward in possession and drops back to defend.','Stamina'),
    'holding':('Defansif orta saha','Holding midfielder','Stoperlerin önündeki alanı tutar.','Screens the centre-backs.','Positioning'),
    'winger':('Çizgi kanadı','Touchline winger','Geniş kalıp çizgide pas ister.','Stays wide and offers an outlet on the flank.','Crossing'),
    'inside_winger':('İçe kat eden kanat','Inside winger','Top sizdeyken merkeze ve kaleye yaklaşır.','Moves inside and towards goal in possession.','Dribbling'),
    'target':('Hedef santrfor','Target forward','Doğrudan paslara ve hava toplarına hedef olur.','Offers a target for direct passes and aerial balls.','Strength'),
    'dropping':('Derine gelen forvet','Dropping forward','Derine gelerek orta sahaya pas bağlantısı sunar.','Drops towards midfield to offer a passing link.','First touch'),
    'finisher':('Bitirici forvet','Finisher','Savunma arkasına ve kaleye koşu arar.','Looks to run behind the defence and towards goal.','Anticipation'),
}


def roles_for(position):
    if position in FULLBACKS:return ('defensive_back','wingback')
    if position in CENTRE_BACKS:return ('stopper','ball_playing')
    if position in ('DM','CM','AM'):return ('ball_winner','playmaker','box_to_box','holding')
    if position in ('RM','LM','RW','LW'):return ('winger','inside_winger')
    if position in ('ST','CF','SS'):return ('target','dropping','finisher')
    return ()


def role_factor(profiles,pid,role,condition,fit):
    skill=profiles[pid][ROLES[role][4]]
    return (.78+skill*.022)*(.65+fit*.0875)*(.78+condition*.0022)


def eligible_role(p,position,role):
    return role in roles_for(position) and fit_level(p,position)>=1
