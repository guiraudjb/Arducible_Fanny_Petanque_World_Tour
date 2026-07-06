local functions = {}  --(*1)
endTimer=endLenght
timerCountEnd = 0
oldTimerCountEnd = 0
--***********************update function*****************************
function functions.endingUpdate()
timerCountEnd = love.timer.getTime( )
	if timerCountEnd >= oldTimerCountEnd + 1 then
	--print(timerCountEnd)
		endTimer = endTimer-1
	oldTimerCountEnd = love.timer.getTime( )
	end
end


--***********************draw function*****************************
function functions.endingDraw()
love.graphics.setFont(mainFont)
love.graphics.print(endTimer,0,0)
love.graphics.printf( grade, screenWidth*1/4, screenHeight*15/100, screenWidth*50/100, "center")
	if playerRank > 0 then
	love.graphics.draw(ranks, rank[playerRank],screenWidth*50/100, screenHeight*50/100,0,ranksFinalScale,ranksFinalScale,17,17)
	end
love.graphics.printf( "SCORE: "..finalScore, screenWidth*1/5, screenHeight*80/100, screenWidth*60/100, "center")

end

return functions --(*2)
