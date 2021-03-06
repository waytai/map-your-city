from mapyourcity import app, db
from mapyourcity.models import Player, HistoryGeo, Game, Team, Scores, History, Game_mp_ffa
from flask import Flask, request, session, g, jsonify, redirect, url_for, abort, render_template, flash
from datetime import datetime
import json

# COMMENTS
@app.before_request
def before_request():
  g.player = None
  if 'player_id' in session:
    g.player = Player.query.filter_by(id = str(session['player_id'])).first()

# COMMENTS
@app.route('/')
def main():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('main.html')

# COMMENTS
@app.route('/login', methods=['GET', 'POST'])
def login():
  error = None
  if request.method == 'POST':
    player = Player.query.filter_by(username = request.form['username']).first()
    if player is not None and player.check_password(request.form['password']):
      session['player_id'] = player.id
      player.set_last_login()
      return redirect(url_for('main'))
    else:
      error = 'Wrong Username or Password'
  else:
    flash('Already logged in')
  return render_template('login.html', error = error)

# COMMENTS
@app.route('/register', methods=['POST','GET'])
def register():
  error = None
  if request.method == 'POST':
    if not request.form['username']:
      error = 'You have to enter a username'
    elif not request.form['email'] or \
      '@' not in request.form['email']:
      error = 'You have to enter a valid email address'
    elif not request.form['password']:
      error = 'You have to enter a password'
    elif request.form['password'] != request.form['password2']:
      error = 'The two passwords do not match'
    elif Player.query.filter_by(username = request.form['username']).first() is not None:
      error = 'The username is already taken'
    else:
      g.player=None
      player = Player(request.form['username'], request.form['email'], request.form['password'])
      db.session.add(player)
      db.session.commit()
      flash('Successfully registered!')
      return redirect(url_for('login'))
  return render_template('register.html', error=error)

# COMMENTS
@app.route('/logout')
def logout():
  session.pop('player_id', None)
  g.player = None
  return redirect(url_for('login'))

# COMMENTS
@app.route('/verify-osm')
def verifyOsm():
  if not g.player:
    return redirect(url_for('login'))
  object_id=  request.args.get('ObjectId', 0, type=int)
  object_name = request.args.get('ObjectName', '', type=str)
  object_type = request.args.get('ObjectType', '', type=str)
  object_latlng = request.args.get('ObjectLatLng', '', type=str)
  object_attribute = []
  object_attribute.append(request.args.get('ObjectAttrWheel', '', type=str))
  object_attribute.append(request.args.get('ObjectAttrVeg', '', type=str))
  object_attribute.append(request.args.get('ObjectAttrSmo', '', type=str))
  score = History(g.player.game.id, g.player.id,'osm')
  history_id = g.player.score.update(1)
  geo = HistoryGeo(history_id, object_id, object_name, object_type, object_attribute, object_latlng)
  db.session.add(score)
  db.session.add(geo)
  db.session.commit()
  return jsonify(result=g.player.score.score_game)

# COMMENTS
@app.route('/setup/sp/ffa')
def setup_sp_ffa():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('setup_sp_ffa.html')

# COMMENTS
@app.route('/sp/ffa')
def sp_ffa():
  if not g.player:
    return redirect(url_for('login'))
  #session['GameID'] = GameSp.query.filter_by(session_start=now).id
  #restaurant = request.args.get('restaurant', 0, type=str)
  #bar = request.args.get('bar', 0, type=str)
  #bank = request.args.get('bank', 0, type=str)
  #radius = request.args.get('radius', 0, type=int)
  g.player.game = Game(g.player.id, 'graz', 1, 'ffa')
  g.player.game.set_objecttypes(True, True, True)
  #g.player.game.set_radius(radius)
  db.session.commit()  
  return render_template('game_sp_ffa.html')

# COMMENTS
@app.route('/sp/motw')
def sp_motw():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('game_sp_motw.html')

# COMMENTS
@app.route('/setup/mp/ffa')
def setup_mp_ffa():
  if not g.player:
    return redirect(url_for('login'))
  '''if request.method == 'POST':
    if not request.form['gametitle']:
      error = 'You have to enter a game title'
    else:
      if g.player.game is not None:
        g.player.game.close_game()
      g.player.game = Game(g.player.id, request.form['gameregion'],2, 'ffa')
      g.player.game.gamempffa = Game_mp_ffa('Testgame',10, 'password', 4, 4,True,True,False)
      db.session.commit()'''
      #return redirect(url_for('login'))
  return render_template('setup_mp_ffa.html', Games = Game.query.filter_by(is_active=True))

@app.route('/setup/mp/ffa/create')
def create_mp_ffa():
  if not g.player:
    return jsonify(result="You must be logged in to create a game!")
  game_name = request.args.get('GameName', '',str)
  game_region = request.args.get('GameRegion', '',str)
  game_duration = request.args.get('GameDuration', 0,int)
  game_secret = request.args.get('GameSecret', '',str)
  game_maxteams = request.args.get('GameMaxTeams', 0,int)
  game_maxplayers = request.args.get('GameMaxPlayers', 0,int)
  game_object_restaurant = request.args.get('GameObjectRestaurant',bool)
  game_object_bar = request.args.get('GameObjectBar',bool)
  game_object_bank = request.args.get('GameObjectBank',bool)
  if g.player.game is not None:
    g.player.game.close_game()
  g.player.game = Game(g.player.id, game_region,2, 'ffa')
  g.player.game.gamempffa = Game_mp_ffa(game_name,game_duration,game_secret, game_maxteams, game_maxplayers,game_object_restaurant,game_object_cafe,game_object_bar,game_object_snack)
  for i in range(game_maxteams):
    g.player.game.team = Team(g.player.game.id, 'Team '+str(i+1), '#', g.player.game)
  g.player.game.gamempffa = Game_mp_ffa(game_name,game_duration,game_secret, game_maxteams, game_maxplayers,game_attribute_wheelchair,game_attribute_smoking,game_attribute_vegetarian,game_object_restaurant,game_object_cafe,game_object_bar,game_object_snack)
  db.session.commit()
  return jsonify(result=g.player.game.gamempffa.name)

@app.route('/mp/ffa/update')
def mp_ffa_update():
  if not g.player:
    return jsonify(result="You must be logged in to create a game!")
  playerLat = request.args.get('PlayerLat',int)
  playerLng = request.args.get('PlayerLng',int)
  g.player.set_position(playerLat,playerLng)
  db.session.commit();
  response='{"players":['
  for player in g.player.game.players.all():
    if player.lat is not None:
      response += '{"username":"'+player.username+'" , "lat":"'+str(player.lat)+'","lng":"'+str(player.lng)+'"},'
  response+=']}'
  return json.dumps(response)

@app.route('/setup/mp/ffa/joingame/<int:gameid>')
def setup_mp_ffa_joingame(gameid):
  if not g.player:
    return 'Error'
  g.player.game = Game.query.filter_by(id=gameid).first()
  db.session.commit()
  teams = g.player.game.teams.all()
  return render_template('setup_mp_ffa_jointeam.html',teams = teams )

@app.route('/setup/mp/ffa/jointeam/<int:teamid>')
def setup_mp_ffa_jointeam(teamid):
  error=''
  if not g.player:
    error='You must be logged in!'
    return render_template('login.html', error = error)
  if not g.player.game:
    error ='You must create or join a game'
    return render_template('setup_mp_ffa.html', Games = Game.query.filter_by(is_active=True),error=error)
  g.player.game.team = Team.query.filter_by(id=teamid).first()
  db.session.commit()
  return redirect(url_for('setup_mp_ffa_waitinghall'))

@app.route('/setup/mp/ffa/waitinghall')
def setup_mp_ffa_waitinghall():
  error=''
  if not g.player:
    error='You must be logged in!'
    return render_template('login.html', error = error)
  if not g.player.game:
    error ='You must create or join a game'
    return render_template('setup_mp_ffa.html', Games = Game.query.filter_by(is_active=True),error=error)
  if not g.player.team:
    error ='You must join a team'
    return render_template('setup_mp_ffa_jointeam.html', Games = Game.query.filter_by(is_active=True),error=error)
  return render_template('setup_mp_ffa_waitinghall.html',teams = teams )


@app.route('/setup/mp/ffa/getgames')
def setup_mp_ffa_getgames():
  if not g.player:
    return jsonify(result="You must be logged in to create a game!")
  print 'test'
  response='{"games":['
  for game in Game.query.filter_by(is_active=True):
    print game.gamempffa.name
    response += '{"gamename":"'+game.gamempffa.name+'" , "region":"'+game.region+'","duration":"'+str(game.gamempffa.duration)+'"},'
  response+=']}'
  return json.dumps(response)

# COMMENTS
@app.route('/mp/ffa')
def mp_ffa():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('game_mp_ffa.html')


# COMMENTS
@app.route('/player')
def player():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('player.html')

# COMMENTS
# @app.route('/player/<playerid>')

# COMMENTS
# @app.route('/player/<playerid>/settings')

# COMMENTS
# @app.route('/player/<playerid>/settings/osm')

# COMMENTS
# @app.route('/player/<playerid>/map-of-fame')

# COMMENTS
# @app.route('/player/<playerid>/score')

# COMMENTS
# @app.route('/player/<playerid>/stats')

# COMMENTS
#@app.route('/<playerid>/settings')
#def playerSettings():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('game.html')

#@app.route('/player/settings')
#def playerSettings():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('game.html')

# COMMENTS
@app.route('/scores')
def scores():
  if not g.player:
    return redirect(url_for('login'))
  #if(datetime.weekday()==1):
    #Player.query.get().all().scores.all().reset_points_week()
  #scores=Scores.query.order_by('score_all desc').limit(10)
  #players = g.player.game.players.all()
  #return render_template('scores.html', Players=players)
  scores = Scores.query.order_by('score_all desc').limit(10)
  return render_template('scores.html', Scores=scores)

# COMMENTS
# @app.route('/score/<playerid>')
# def scorePlayer():
#   if not g.player:
#     return redirect(url_for('login'))
#  return render_template('score.html')

# COMMENTS
#@app.route('/score/<region>')
#def scoreRegion():
  #if not g.player:
#    return redirect(url_for('login'))
  #return render_template('score.html')

# COMMENTS
#@app.route('/score/<country>')
#def scoreCountry():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('score.html')

# COMMENTS
@app.route('/scores/world')
def scoreWorld():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('scores.html')

# COMMENTS
@app.route('/about')
def about():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('about.html')

# COMMENTS
#@app.route('/about/terms-of-use')
#def aboutTou():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('about.html')

# COMMENTS
#@app.route('/about/code')
#def aboutCode():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('about.html')

# COMMENTS
#@app.route('/about/gamemodi')
#def aboutGamemodi():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('help.html')

# COMMENTS
#@app.route('/about/gamemodi/sp_motw')
#def aboutGamemodiSpMotw():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('help.html')

# COMMENTS
#@app.route('/about/gamemodi/sp_ffa')
#def aboutGamemodiSpFfa():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('help.html')

# COMMENTS
#@app.route('/about/data-protection')
#def aboutDataProtection():
#  if not g.player:
#    return redirect(url_for('login'))
#  return render_template('about.html')

# COMMENTS
@app.route('/help')
def help():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('help.html')

# COMMENTS
@app.route('/help/sp/ffa')
def help_sp_ffa():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('help_sp_ffa.html')

# COMMENTS
@app.route('/help/mp/ffa')
def help_mp_ffa():
  if not g.player:
    return redirect(url_for('login'))
  return render_template('help_mp_ffa.html')

