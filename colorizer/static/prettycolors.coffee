TAU = Math.PI*2

makeRGB = (triple) ->
  [r, g, b] = triple
  return "rgb(#{r}, #{g}, #{b})"

class RenderedWord
  initialize: (x, y, size, colors) ->
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
    size = 
    ctx.font = 

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
    @words = (w for w in @words if w.alpha > 0.1)
  
  handleResponse: (obj) ->

this.PrettyColors = PrettyColors
