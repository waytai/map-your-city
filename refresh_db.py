from mapyourcity import app, db
from mapyourcity.models import Player, OsmObjects, Regions
db.drop_all()
db.create_all()
obj1 = Regions(region_short='graz', region_full='Stadt Graz', country_short='at', country_full='Austria')
db.session.add(obj1)
obj2 = Player(username='cheeseman', email='test@test.at', password='test')
db.session.add(obj2)
obj3 = OsmObjects(title='amenity=restaurant', full_name='Restaurant')
db.session.add(obj3)
obj4 = OsmObjects(title='amenity=bar', full_name='Bar')
db.session.add(obj4)
obj5 = OsmObjects(title='amenity=bank', full_name='Bank')
db.session.add(obj5)
obj6=Scores(username='cheeseman', user_id='1')
db.session.add(obj6)
db.session.commit()
exit()
