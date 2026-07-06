local functions = {}  --(*1)
helpReading=false
introTimer=IntroLenght
timerCountIntro = 0
oldTimerCountIntro = 0

--******************update functions****************************
    function functions.updateIntroContdown()
	timerCountIntro = love.timer.getTime( )
	if timerCountIntro >= oldTimerCountIntro + 1 then
	--print(timerCountIntro)
		introTimer = introTimer-1
	oldTimerCountIntro = love.timer.getTime( )
	end

end

--******************draw functions******************************

function functions.helpDrawItemInformations()
love.graphics.draw(targets, target[2], screenWidth/4, screenHeight*20/100,0,targetFinalScale*targetAnimatingScaler/100,targetFinalScale*targetAnimatingScaler/100,18,18)
love.graphics.draw(targets, target[1], screenWidth*3/4, screenHeight*20/100,0,targetFinalScale,targetFinalScale,18,18)

love.graphics.draw(timeExtenders, timeExtender[1],screenWidth*20/100, screenHeight*50/100,0,timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.FinalScale*sizeTimeExtender/100,14,14)
love.graphics.draw(timeExtenders, timeExtender[2],screenWidth*20/100, screenHeight*60/100,0,timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.FinalScale*sizeTimeExtender/100,14,14)
love.graphics.draw(timeExtenders, timeExtender[3],screenWidth*20/100, screenHeight*70/100,0,timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.FinalScale*sizeTimeExtender/100,14,14)
love.graphics.draw(timeExtenders, timeExtender[4],screenWidth*20/100, screenHeight*80/100,0,timeExtender.FinalScale*sizeTimeExtender/100,timeExtender.FinalScale*sizeTimeExtender/100,14,14)

love.graphics.setFont(helpFont)
love.graphics.printf("HIT THE BALLS", screenWidth*30/100, screenHeight*1/5, screenWidth*40/100, "center")
love.graphics.printf("GAME INFORMATION", screenWidth*1/5, screenHeight*2/100, screenWidth*60/100, "center")
love.graphics.printf("+1 PT", screenWidth*1/8, screenHeight*30/100, screenWidth*1/4, "center")
love.graphics.printf("-1 PT BE CAREFUL", screenWidth*1/2, screenHeight*30/100, screenWidth*1/2, "center")
love.graphics.printf("-----------BONUS-----------", screenWidth*1/5, screenHeight*40/100, screenWidth*60/100, "center")
love.graphics.printf("+1 PT  + 30S TIME EXTENTION", screenWidth*1/5, screenHeight*50/100, screenWidth*60/100, "center")
love.graphics.printf("+2 PTS + 45S TIME EXTENTION", screenWidth*1/5, screenHeight*60/100, screenWidth*60/100, "center")
love.graphics.printf("+3 PTS + 60S TIME EXTENTION", screenWidth*1/5, screenHeight*70/100, screenWidth*60/100, "center")
love.graphics.printf("+4 PTS + THE ROCK OF HAZARD", screenWidth*1/5, screenHeight*80/100, screenWidth*60/100, "center")
love.graphics.printf("MAYBE GOOD OR BAD", screenWidth*1/5, screenHeight*90/100, screenWidth*60/100, "center")
love.graphics.printf("GET READY IN "..introTimer,screenWidth*1/4, screenHeight*10/100, screenWidth*1/2, "center")
end





return functions --(*2)
