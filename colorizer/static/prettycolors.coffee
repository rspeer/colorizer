TAU = Math.PI*2

makeRGBA = (triple, alpha) ->
  [r, g, b] = triple
  return "rgba(#{r}, #{g}, #{b}, #{alpha})"

class RenderedWord
  initialize: (word, x, y, size, colors) ->
    @word = word
    @x = x
    @y = y
    @colors = colors
    @angle = Math.random() * TAU
    @radius = 2
    @alpha = 1
    @vx = 0
    @vy = 0
    @ay = Math.random()/40 + 0.1
    @rotationRate = Math.random() + 1
    @size = size
    @fadeRate = 0.995

  step: () ->
    @y -= @vy
    @radius += @vy*2
    @vy += @ay

    @x += @vx
    @vx += Math.random()/10

    @angle += @rotationRate
    if @angle > TAU
      @angle -= TAU

    @alpha *= @fadeRate
    @size /= @fadeRate

  draw: (ctx) ->
    ctx.font = "#{@size}px Helvetica"
    if @colors.length == 0
      ctx.fillStyle = '#888'
    else
      ctx.fillStyle = makeRGBA(@colors[@colors.length-1], @alpha)
    ctx.fillText(@word, @x, @y)
    
    if @colors.length > 0
      for i in [0...@colors.length-1]
        ctx.fillStyle = makeRGBA(@colors[i], @alpha*@alpha)
        ctx.fillText(@word, @x + @r * Math.cos(@angle), @y + @r * Math.sin(@angle))

class PrettyColors
  initialize: () ->
    @canvas = $('#textarea')[0]
    @canvas.width = window.innerWidth
    @canvas.height = window.innerHeight
    @ctx = @canvas.getContext "2d"
    @uid = ''+Math.floor(Math.random() * 10000)

    @xPos = 0
    @words = []

  sendText: (text) ->
    escapedText = encodeURI(text.replace(/[\/ ]/g, '+'))
    $.ajax
      url: "/input/#{@uid}/#{escapedText}"
      dataType: 'json'
      success: @handleResponse

  cleanWords: ->
    @words = (w for w in @words when w.alpha > 0.1 and w.y > 0)
  
  handleResponse: (obj) ->
    size = 10 + obj.weight/100
    newWord = new RenderedWord(
    	obj.active,
    	@xPos,
    	@canvas.height/2 + Math.random()*20 - 10,
    	10 + obj.weight/50,
    	obj.activeColors
    )
    @words.push newWord
    @xPos += size*6
    if @xPos + size*6 > @canvas.width
      @xPos += size*6
      @xPos -= @canvas.width

this.PrettyColors = PrettyColors
