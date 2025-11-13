use std::collections::HashMap;

use pyo3::prelude::*;

use optimize::optimize;

mod optimize;
mod spriter;

#[pyfunction]
fn svg_sprite(svgs: Vec<HashMap<String, String>>, dest: String) {
    let optimized_svgs = svgs
        .iter()
        .map(|svg| {
            let mut map = HashMap::new();
            let id = svg.get("id").unwrap();
            let content = svg.get("content").unwrap();
            let optimized_content = optimize(content);
            map.insert("id".to_string(), id.to_string());
            map.insert("content".to_string(), optimized_content.to_string());
            map
        })
        .collect::<Vec<HashMap<String, String>>>();

    spriter::process(optimized_svgs, dest)
}

#[pyfunction]
fn svg_optimize(source: String) -> String {
    optimize(&source)
}

/// A Python module implemented in Rust.
#[pymodule]
fn svg_spriter_py(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(svg_sprite, m)?)?;
    m.add_function(wrap_pyfunction!(svg_optimize, m)?)?;
    Ok(())
}

#[cfg(test)]
mod test {
    use super::svg_sprite;
    use std::collections::HashMap;

    #[test]
    fn test() {
        let mut map = HashMap::new();

        map.insert("id".to_string(), "0".to_string());
        map.insert("content".to_string(), "<?xml version='1.0' standalone='no'?>\n<!DOCTYPE svg PUBLIC '-//W3C//DTD SVG 20001102//EN'\n'http://www.w3.org/TR/2000/CR-SVG-20001102/DTD/svg-20001102.dtd'>\n<svg xmlns='http://www.w3.org/2000/svg' width='184' height='48'\n\txmlns:sodipodi='http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'>\n<desc>wmf2svg</desc>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:23.609713; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 36.653385 18.179480)'\n\t>(</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:23.609713; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 74.243469 18.179480)'\n\t>)</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:23.609713; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 105.561752 18.179480)'\n\t>(</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:23.609713; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 142.907486 18.179480)'\n\t>)</text>\n<line x1='23.213812' y1='25.267088' x2='148.568390' y2='25.267088' \n\tstyle='stroke-width:0.832806; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:none; stroke:black' />\n<text x='0' y='0' style='font-family:Times; font-style:normal; font-weight:normal; font-size:10.420192; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 15.353696 40.193306)'\n\t>0</text>\n<text x='0' y='0' style='font-family:Times; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 0.000000 29.773115)'\n\t>l</text>\n<text x='0' y='0' style='font-family:Times; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 4.154050 29.773115)'\n\t>i</text>\n<text x='0' y='0' style='font-family:Times; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 8.552457 29.773115)'\n\t>m</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:10.420192; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 1.629039 40.193306)'\n\t>x</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 27.123507 16.865221)'\n\t>f</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 43.128819 16.865221)'\n\t>a</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 66.098274 16.865221)'\n\t>x</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 96.031876 16.865221)'\n\t>f</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 112.037186 16.865221)'\n\t>a</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 134.762283 16.865221)'\n\t>x</text>\n<text x='0' y='0' style='font-family:Times; font-style:italic; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 82.836655 43.854458)'\n\t>x</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:10.420192; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 6.149624 40.193306)'\n\t></text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 53.880478 16.865221)'\n\t>+</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 81.859230 16.865221)'\n\t>-</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 122.788841 16.865221)'\n\t>-</text>\n<text x='0' y='0' style='font-family:Symbol; font-style:normal; font-weight:normal; font-size:18.024115; fill:black' transform='matrix(1.000000 -0.000000 0.000000 1.000000 152.722443 29.773115)'\n\t>=</text>\n</svg>\n".to_string());

        let data = vec![map];

        svg_sprite(data, "abc.svg".to_string());
    }
}
