local functions = {}  --(*1)
--mainFont=""
--helpFont=""
function functions.loadFonts()
	mainFont = love.graphics.newFont("fonts/ARCADE_I.TTF",screenWidth*3/100)
	helpFont = love.graphics.newFont("fonts/ARCADE_I.TTF",screenWidth*2/100)
end


return functions --(*2)
