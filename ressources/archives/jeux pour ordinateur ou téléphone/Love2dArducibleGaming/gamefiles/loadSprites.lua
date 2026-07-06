local functions = {}  --(*1)
target = {}
timeExtender = {}
rank = {}

function functions.loadSprites()
	targets = love.graphics.newImage("sprites/targets.png")
	targetWidth = 36
	targetHeight = 36
	targetFinalWidth = screenWidth*12/100
	targetFinalScale = targetFinalWidth/targetWidth
	targetFinalHeight=targetHeight*targetFinalScale
		for b = 1,4 do
			target[b]=love.graphics.newQuad((b-1)*targetWidth, 0, targetWidth, targetHeight, targets:getDimensions())
		end

	timeExtenders = love.graphics.newImage("sprites/timeExtender.png")
  timeExtender = {}
	timeExtender.Width  = 34
	timeExtender.Height = 34
	timeExtender.FinalWidth = screenWidth*5/100
	timeExtender.FinalScale = timeExtender.FinalWidth/timeExtender.Width
	timeExtender.FinalHeight = timeExtender.Height* timeExtender.FinalScale
	timeExtender.TranslateWidth = targetFinalWidth*3/4
	timeExtender.TranslateHeight = targetFinalHeight*3/4
  timeExtender.Posx = 0
  timeExtender.Posy = - timeExtender.TranslateHeight/2
  timeExtender.Movx = 2
  timeExtender.Movy = 0
  timeExtender.Direction = 1
  timeExtender.position ="front"
  timeExtender.scalex = 0.5

			for b = 1,4 do
			timeExtender[b]=love.graphics.newQuad((b-1)*timeExtender.Width, 0, timeExtender.Width, timeExtender.Height, timeExtenders:getDimensions())
		end

	ranks = love.graphics.newImage("sprites/rank.png")
	ranksWidth  = 34
	ranksHeight = 34
	ranksFinalWidth = screenWidth*15/100
	ranksFinalScale = ranksFinalWidth/ranksWidth
	ranksFinalHeight = ranksHeight * ranksFinalScale 
	for b = 1,4 do
			rank[b]=love.graphics.newQuad((b-1)*ranksWidth, 0, ranksWidth, ranksHeight, ranks:getDimensions())
	end
	bang = love.graphics.newImage( "sprites/Explosion.png")
	bangWidth = 256
	bangHeight = 256
	bangFinalWidth = screenWidth*15/100
	bangFinalScale = bangFinalWidth/bangWidth
	bangFinalHeight = bangHeight*bangFinalScale
	
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

function functions.backgroundDraw()
	love.graphics.draw(background,0,0,0,screenWidth/backgroundWidth,screenHeight/backgroundHeight)
end

return functions --(*2)
