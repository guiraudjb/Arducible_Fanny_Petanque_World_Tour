components {
  id: "GameInfo"
  component: "/Scripts/GameInfo.script"
  position {
    x: 0.0
    y: 0.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  property_decls {
  }
}
embedded_components {
  id: "Bonus2Text"
  type: "label"
  data: "size {\n  x: 800.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 1.0\n  z: 1.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_W\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"+2 PT + 45s TIME EXTENTION\"\nfont: \"/GameObjects/labels/SmallArcadeFont.font\"\nmaterial: \"/builtins/fonts/label-df.material\"\n"
  position {
    x: -336.0
    y: -128.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "sprite"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"1000x800\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: 0.0
    y: 0.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "Bonus3Text"
  type: "label"
  data: "size {\n  x: 800.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 1.0\n  z: 1.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_W\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"+3 PT + 60s TIME EXTENTION\"\nfont: \"/GameObjects/labels/SmallArcadeFont.font\"\nmaterial: \"/builtins/fonts/label-df.material\"\n"
  position {
    x: -336.0
    y: -256.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "Bonus4Text"
  type: "label"
  data: "size {\n  x: 800.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 1.0\n  z: 1.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_W\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"+4 PT   THE ROCK OF HASARD\"\nfont: \"/GameObjects/labels/SmallArcadeFont.font\"\nmaterial: \"/builtins/fonts/label-df.material\"\n"
  position {
    x: -336.0
    y: -384.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "Bonus1Text"
  type: "label"
  data: "size {\n  x: 800.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 1.0\n  z: 1.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_W\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"+1 PT + 30s TIME EXTENTION\"\nfont: \"/GameObjects/labels/SmallArcadeFont.font\"\nmaterial: \"/builtins/fonts/label-df.material\"\n"
  position {
    x: -336.0
    y: 0.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "GreenBall"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"BouleG\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: -320.0
    y: 210.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 2.0
    y: 2.0
    z: 1.0
  }
}
embedded_components {
  id: "GreenBallLabel"
  type: "label"
  data: "size {\n  x: 128.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 1.0\n  z: 1.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_CENTER\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"+1 PT\"\nfont: \"/GameObjects/labels/SmallArcadeFont.font\"\nmaterial: \"/builtins/fonts/label.material\"\n"
  position {
    x: -320.0
    y: 100.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "Bonus2"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"extending23\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: -400.0
    y: -128.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 0.8
    y: 0.8
    z: 1.0
  }
}
embedded_components {
  id: "GreyBallLabel"
  type: "label"
  data: "size {\n  x: 128.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 1.0\n  z: 1.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_CENTER\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"-1 PT\"\nfont: \"/GameObjects/labels/SmallArcadeFont.font\"\nmaterial: \"/builtins/fonts/label.material\"\n"
  position {
    x: 320.0
    y: 100.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
}
embedded_components {
  id: "GreyBall"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"boule\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: 320.0
    y: 210.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 2.0
    y: 2.0
    z: 1.0
  }
}
embedded_components {
  id: "bonus4"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"extending43\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: -400.0
    y: -384.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 0.8
    y: 0.8
    z: 1.0
  }
}
embedded_components {
  id: "Bonus3"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"extending33\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: -400.0
    y: -256.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 0.8
    y: 0.8
    z: 1.0
  }
}
embedded_components {
  id: "Bonus1"
  type: "sprite"
  data: "tile_set: \"/assets/GameSprites.atlas\"\ndefault_animation: \"extending13\"\nmaterial: \"/builtins/materials/sprite.material\"\nblend_mode: BLEND_MODE_ALPHA\n"
  position {
    x: -400.0
    y: 0.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 0.8
    y: 0.8
    z: 1.0
  }
}
embedded_components {
  id: "TitleGame"
  type: "label"
  data: "size {\n  x: 0.0\n  y: 32.0\n  z: 0.0\n  w: 0.0\n}\ncolor {\n  x: 1.0\n  y: 0.84313726\n  z: 0.0\n  w: 1.0\n}\noutline {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nshadow {\n  x: 0.0\n  y: 0.0\n  z: 0.0\n  w: 1.0\n}\nleading: 1.0\ntracking: 0.0\npivot: PIVOT_CENTER\nblend_mode: BLEND_MODE_ALPHA\nline_break: false\ntext: \"ARDUCIBLE\\n\"\n  \"PETANQUE\\n\"\n  \"SHOOTING\"\nfont: \"/GameObjects/labels/ArcadeFont.font\"\nmaterial: \"/builtins/fonts/label-df.material\"\n"
  position {
    x: 5.0
    y: 367.0
    z: 0.0
  }
  rotation {
    x: 0.0
    y: 0.0
    z: 0.0
    w: 1.0
  }
  scale {
    x: 0.8
    y: 1.0
    z: 1.0
  }
}
