components {
  id: "ending"
  component: "/Scripts/ending.script"
}
embedded_components {
  id: "label"
  type: "label"
  data: "size {\n"
  "  x: 800.0\n"
  "  y: 64.0\n"
  "}\n"
  "text: \"Try Again\"\n"
  "font: \"/GameObjects/labels/ArcadeFont.font\"\n"
  "material: \"/builtins/fonts/label.material\"\n"
  ""
  position {
    z: 1.0
  }
}
embedded_components {
  id: "label1"
  type: "label"
  data: "size {\n"
  "  x: 128.0\n"
  "  y: 32.0\n"
  "}\n"
  "text: \"SCORE\"\n"
  "font: \"/GameObjects/labels/Title.font\"\n"
  "material: \"/builtins/fonts/label.material\"\n"
  ""
  position {
    y: -150.0
    z: 1.0
  }
}
embedded_components {
  id: "label2"
  type: "label"
  data: "size {\n"
  "  x: 128.0\n"
  "  y: 32.0\n"
  "}\n"
  "text: \"100\"\n"
  "font: \"/GameObjects/labels/Title.font\"\n"
  "material: \"/builtins/fonts/label.material\"\n"
  ""
  position {
    y: -400.0
    z: 1.0
  }
}
