local functions = {}  --(*1)


function functions.keyboardRead()

	if love.keyboard.isDown("return") then
		gameState = gameState + 1
		backgroundLoad = false
		love.timer.sleep( 1 )
	end
   
	if love.keyboard.isDown("escape") then
		love.event.quit()
	end
	
	
	if love.keyboard.isDown("up") then
		os.execute("amixer set Master 5%+")
	end
	
	if love.keyboard.isDown("down") then
		os.execute("amixer set Master 5%-")
	end
		
	if love.keyboard.isDown("right") then
		firstInit()
	end
	
		if love.keyboard.isDown("left") then
		love.audio.stop( Starcade )
		if playingMusic == true then
		playingMusic=false
		else
		playingMusic=true
		end
		end
	
	
	if love.keyboard.isDown("e") then
		target1 = true
		targetHited=true
	else
		target1 = false
	end

	if love.keyboard.isDown("r") then
		target2 = true
		targetHited=true
	else
		target2 = false
	end

	if love.keyboard.isDown("t") then
		target3 = true
		targetHited=true
	else
		target3 = false
	end
	

end


return functions --(*2)
