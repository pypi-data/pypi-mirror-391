use std::{collections::HashMap, fs, path::Path};

use xmltree::{Element, EmitterConfig, Namespace, XMLNode};

// const EXCLUDE_ATTRS: [&str; 2] = ["fill", "stroke"]; 

#[derive(Debug)]
pub struct Svg {
    pub id: String,
    pub content: String,
}

impl From<HashMap<String, String>> for Svg {
    fn from(map: HashMap<String, String>) -> Self {
        let id = map.get("id").unwrap_or(&String::from("")).to_string();
        let content = map.get("content").unwrap_or(&String::from("")).to_string();
        Self { id, content }
    }
}

pub fn process<T, P>(svgs: Vec<T>, dest: P)
where
    T: Into<Svg>,
    P: AsRef<Path>,
{
    let mut svg = Element::new("svg");
    let mut namespaces = Namespace::empty();

    namespaces.put("", "http://www.w3.org/2000/svg");
    namespaces.put("xlink", "http://www.w3.org/1999/xlink");

    svg.namespaces = Some(namespaces);
    svg.attributes
        .insert(String::from("class"), String::from("_SVG_LMS_FORMULA_"));
    svg.attributes
        .insert(String::from("aria-hidden"), String::from("true"));
    svg.attributes.insert(
        String::from("style"),
        String::from("position: absolute; width: 0; height: 0"),
    );

    svgs.into_iter().for_each(|item| {
        let s: Svg = item.into();
        if let Ok(svg_root_element) = Element::parse(s.content.as_bytes()) {
            let mut new_svg_element = Element::new("symbol");

            let view_box = svg_root_element.attributes.get_key_value("viewBox");
            if let Some((k, v)) = view_box {
                new_svg_element
                    .attributes
                    .insert(k.to_owned(), v.to_owned());
            }
            let width = svg_root_element.attributes.get("width");
            let height = svg_root_element.attributes.get("height");

            if let (None, Some(w), Some(h)) = (view_box, width, height) {
                new_svg_element
                    .attributes
                    .insert(String::from("viewBox"), format!("0,0,{},{}", w, h));
            }

            fn invoke(element: Element) -> Element {
                let mut element_name = "symbol";
                if element.name != "svg" {
                    element_name = &element.name;
                }

                let mut new_ele = Element::new(element_name);
                let attrs = &element.attributes;
                attrs.iter().for_each(|(k, v)| {
                    new_ele.attributes.insert(k.to_string(), v.to_string());
                });

                element.children.into_iter().for_each(|child| match child {
                    XMLNode::Element(e) => new_ele.children.push(XMLNode::Element(invoke(e))),
                    XMLNode::Text(t) => new_ele.children.push(XMLNode::Text(t)),
                    XMLNode::CData(d) => new_ele.children.push(XMLNode::CData(d)),
                    _ => (),
                });

                new_ele
            }

            let mut new_svg_element = invoke(svg_root_element);

            let mut namespaces = Namespace::empty();
            namespaces.put("", "http://www.w3.org/2000/svg");

            new_svg_element.namespaces = Some(namespaces);

            new_svg_element
                .attributes
                .insert("id".to_owned(), format!("lms-formula-{}", s.id));

            svg.children.push(XMLNode::Element(new_svg_element));
        }
    });

    let h = fs::File::create(dest).unwrap();
    let config = EmitterConfig::default().write_document_declaration(false);

    svg.write_with_config(h, config).unwrap();
}
