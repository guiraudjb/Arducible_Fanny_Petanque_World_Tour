local functions = {}  --(
sizeTimeExtender=100
timeExtenderTimer=0
timeExtenderOldTimer=0
timerCount=0
oldTimerCount=0
targetTimer=0
targetAnimatingScaler=98
bangAnimatingScaler=50

targetOldTimer=0
bangOldTimer=0

target1 = false
target2 = false
target3 = false
targetHited = false
levelProgress = 1
tempPartie=60
bang1Timer=0
bang2Timer=0
bang3Timer=0


function functions.levelLoad(niveau)
--print("run levelLoad")
	--/liberer de la memoire l image precedente/
	levelParameters = ""
	collectgarbage()
	-- fin liberation memoire
	file="levels/"..niveau.."/parameters"
	--print(file)
    levelParameters = require ("levels/"..niveau.."/parameters") --"levels/1/parameters"
    levelParameters.getLevelParameters()
 end

function functions.backgroundLoad(niveau)
--/liberer de la memoire l image precedente/
	background       = ""
	backgroundWidth  = 0
	--print(backgroundWidth)
	backgroundHeight = 0
	collectgarbage()
	-- fin liberation memoire
	background = love.graphics.newImage("levels/"..niveau.."/fond.jpg")
	backgroundWidth = background:getWidth()
	backgroundHeight = background:getHeight()

end


function functions.timeExtenderAnimating()
timeExtenderTimer = love.timer.getTime( )
	if timeExtenderTimer >= timeExtenderOldTimer + 0.05 then
	--print(timer)
		sizeTimeExtender=sizeTimeExtender+2
			if sizeTimeExtender >100 then
				sizeTimeExtender = 90
			end
timeExtenderOldTimer = love.timer.getTime( )
	end

end

function functions.TargetAnimating()
	targetTimer = love.timer.getTime( )
		if targetTimer >= targetOldTimer + 0.1 then
			targetAnimatingScaler=targetAnimatingScaler+1
				if targetAnimatingScaler >100 then
					targetAnimatingScaler = 97
				end
	targetOldTimer = love.timer.getTime( )
	end

end

function functions.bangAnimating()
	bangTimer = love.timer.getTime( )
		if bangTimer >= bangOldTimer + 0.1 then
			bangAnimatingScaler=bangAnimatingScaler+10
				if bangAnimatingScaler >100 then
					bangAnimatingScaler = 50
				end
	bangOldTimer = love.timer.getTime( )
	end

end


function functions.levelEngine()
if targetHited == true then

	if target1 == true then
  	bangAnimatingScaler = 50
  	bang1Timer = love.timer.getTime( )
		if (activeTarget==1)then
		    hit()
		elseif timeExtending == 1 then
		    timeExtenderAttributing()
		else
		    miss()
		end
  	target1=false
  	timeToWaitKeyboard()
	end

	if target2 == true  then
		bangAnimatingScaler = 50
		bang2Timer = love.timer.getTime( )
		if (activeTarget==2)then
			hit()
		elseif timeExtending == 2 then
		    timeExtenderAttributing()
    else
			miss()
		end
		target2=false
    timeToWaitKeyboard()
	end

	if target3 == true  then
		bangAnimatingScaler = 50
		bang3Timer = love.timer.getTime( )
		if (activeTarget==3)then
			hit()
		elseif timeExtending == 3 then
      timeExtenderAttributing()
		else
			miss()
		end
		target3=false
	  timeToWaitKeyboard()
	end
end
targetHited = false
end

function hit()
	love.audio.play( sonHit )
  score=score+1
  TargetUpdater()

end

function miss()
	love.audio.play( sonBad )
	score=score-1
end

function timeToWaitKeyboard()
	--love.timer.sleep( 1/2 )
	keyBoardTimer = love.timer.getTime() + keyboardDelay
	globalTimer=globalTimer+keyboardDelay
	activeKeyboard = false
end

function TargetUpdater()
	if levelProgress < 3 then
		levelProgress = levelProgress + 1
		activeTarget=levelTargets[levelProgress]
		timeExtending=levelTimeExtenderPositions[levelProgress]
		timeExtendingValue = levelTimeExtenderValues[levelProgress]
		--print("time extending "..timeExtendingValue)

	else
		backgroundLoad = false
		levelProgress = 1
		gameState = gameState + 1
end

end

function functions.updateGameContdown()
  timerCount = love.timer.getTime( )
  	if timerCount >= oldTimerCount + 1 then
  		globalTimer = globalTimer-1
      oldTimerCount = love.timer.getTime( )
  	end

end

function timeExtenderAttributing()
  score = score + timeExtendingValue
  love.audio.play( sonBonus )
		if timeExtendingValue <= 3 then
			globalTimer = globalTimer + 15 + (timeExtendingValue * 15)
		end

		if timeExtendingValue == 4 then
			rockTimer=rng:random(1,30)
			--print(rockTimer)
			hazzard=rng:random(0,1)
			if hazzard == 1 then
						globalTimer = globalTimer + rockTimer
			else
						globalTimer = globalTimer - rockTimer
			end
			--print (hazzard)
			--globalTimer = globalTimer + rockTimer
		end

	timeExtendingValue = 0
	timeExtending = 0

end


function functions.backgroundDraw()
	love.graphics.draw(background,0,0,0,screenWidth/backgroundWidth,screenHeight/backgroundHeight)
end

function functions.targetDraw()
	if (activeTarget==1) then
			love.graphics.draw(targets, target[2], screenWidth/4, screenHeight*4/5,0,targetFinalScale*targetAnimatingScaler/100,targetFinalScale*targetAnimatingScaler/100,18,18)
	else
			love.graphics.draw(targets, target[1], screenWidth/4, screenHeight*4/5,0,targetFinalScale,targetFinalScale,18,18)
	end

  if (activeTarget==2) then
			love.graphics.draw(targets, target[2], screenWidth/2, screenHeight*4/5,0,targetFinalScale*targetAnimatingScaler/100,targetFinalScale*targetAnimatingScaler/100,18,18)
	else
			love.graphics.draw(targets, target[1], screenWidth/2, screenHeight*4/5,0,targetFinalScale,targetFinalHeightScale,18,18)
	end

 	if (activeTarget==3) then
			love.graphics.draw(targets, target[2], screenWidth*3/4, screenHeight*4/5,0,targetFinalScale*targetAnimatingScaler/100,targetFinalScale*targetAnimatingScaler/100,18,18)
	else
			love.graphics.draw(targets, target[1], screenWidth*3/4, screenHeight*4/5,0,targetFinalScale,targetFinalScale,18,18)
	end

if (Warn1 == true) then
	love.graphics.draw(targets, target[4], screenWidth/4, screenHeight*4/5,0,targetFinalScale*targetAnimatingScaler/100,targetFinalScale*targetAnimatingScaler/100,18,18)
end

if (Warn2 == true) then
	love.graphics.draw(targets, target[4], screenWidth/2, screenHeight*4/5,0,targetFinalScale*targetAnimatingScaler/100,targetFinalScale*targetAnimatingScaler/100,18,18)
end

if (Warn3 == true) then
	love.graphics.draw(targets, target[4], screenWidth*3/4, screenHeight*4/5,0,targetFinalScale,targetFinalScale,18,18)
end

end

function functions.bangDraw()
	if love.timer.getTime( ) < bang1Timer + 1 then
		love.graphics.draw(bang,screenWidth*1/4,screenHeight*4/5,0,bangFinalScale*bangAnimatingScaler/100,bangFinalScale*bangAnimatingScaler/100,128,128)
	end

	if love.timer.getTime( ) < bang2Timer + 1 then
		love.graphics.draw(bang,screenWidth*1/2,screenHeight*4/5,0,bangFinalScale*bangAnimatingScaler/100,bangFinalScale*bangAnimatingScaler/100,128,128)
	end

	if love.timer.getTime( ) < bang3Timer + 1 then
		love.graphics.draw(bang,screenWidth*3/4,screenHeight*4/5,0,bangFinalScale*bangAnimatingScaler/100,bangFinalScale*bangAnimatingScaler/100,128,128)
	end
end

function functions.timeExtenderDraw(timeExtenderIndex)
-- facteur d'échelle du timeExtender
local posx = math.abs(timeExtender.Posx)/timeExtender.TranslateWidth -- de 0 à 1 position
local coeffx = math.sqrt(1 - posx)  -- coefficent pour arrondissement de la trajectoire varie de 0 à 1
timeExtender.scalex = 1+(0.4 - posx*0.4)*timeExtender.Direction*coeffx
-- déplacement du timeExtender
timeExtender.Posx = timeExtender.Posx + (timeExtender.Movx)*(coeffx+0.01)
timeExtender.Posy = timeExtender.Posy + timeExtender.Movy

-- Invertion du sens de déplacement
if (math.abs(timeExtender.Posx) >= timeExtender.TranslateWidth) then
	timeExtender.Posx = timeExtender.Posx - (timeExtender.Movx)*(coeffx+0.01)
  	timeExtender.Movx = -timeExtender.Movx
	timeExtender.Direction = - timeExtender.Direction
  if timeExtender.position == "front" then
	
    timeExtender.position = "back"
  else
    timeExtender.position = "front"
  end
end
if (math.abs(timeExtender.Posy) >= timeExtender.TranslateHeight) then
  timeExtender.Movy = - timeExtender.Movy

end




	if (timeExtending==1) then
			love.graphics.draw(timeExtenders, timeExtender[timeExtenderIndex],screenWidth/4+timeExtender.Posx, screenHeight*4/5-timeExtender.Posy*coeffx*timeExtender.Direction,0,timeExtender.scalex*timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.scalex*timeExtender.FinalScale*sizeTimeExtender/100,17,17)
	end


	if (timeExtending==2) then
			love.graphics.draw(timeExtenders, timeExtender[timeExtenderIndex], screenWidth/2+timeExtender.Posx, screenHeight*4/5-timeExtender.Posy*coeffx*timeExtender.Direction,0,timeExtender.scalex*timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.scalex*timeExtender.FinalScale*sizeTimeExtender/100,17,17)
	end


	if (timeExtending==3) then
			love.graphics.draw(timeExtenders, timeExtender[timeExtenderIndex], screenWidth*3/4+timeExtender.Posx, screenHeight*4/5-timeExtender.Posy*coeffx*timeExtender.Direction,0,timeExtender.scalex*timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.scalex*timeExtender.FinalScale*sizeTimeExtender/100,17,17)
	end
end

function functions.inGameInformations(level)
love.graphics.setFont(mainFont)
love.graphics.print( "TIME LEFT : "..globalTimer, screenWidth*5/100,screenHeight*0/100,0,1,1 )
love.graphics.print( "LEVEL     : "..level, screenWidth*5/100,screenHeight*15/100,0,1,1 )
love.graphics.print( "SCORE     : "..score, screenWidth*5/100,screenHeight*30/100,0,1,1 )
love.graphics.print( "Int: "..intermediaire, screenWidth*70/100,screenHeight*0/100,0,1,1 )
if activeKeyboard == true then
love.graphics.print( "GO", screenWidth*70/100,screenHeight*20/100,0,1,1 )
else
love.graphics.print( "WAIT", screenWidth*70/100,screenHeight*20/100,0,1,1 )
end
end


return functions --(*2)
