local functions = {}  --(*1)
function functions.soundLoad()
	sonHit = love.audio.newSource("sound/son1.wav", "stream")
	sonBonus = love.audio.newSource("sound/son3.ogg", "stream")
	sonBad = love.audio.newSource("sound/son2.wav", "stream")
	Starcade = love.audio.newSource("music/BlueNavi-Starcade.mp3", "stream")
end


return functions --(*2)
