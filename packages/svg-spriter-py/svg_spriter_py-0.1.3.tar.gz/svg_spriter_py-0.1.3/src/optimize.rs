use svgcleaner::{cleaner, CleaningOptions, ParseOptions, StyleJoinMode, WriteOptions};

#[allow(dead_code)]
pub fn optimize(raw: &String) -> String {
    // 定义解析选项（更严格，避免无效内容）
    let parse_option = ParseOptions {
        parse_comments: true,
        parse_declarations: true,
        parse_unknown_elements: false, // 不解析未知元素
        parse_unknown_attributes: false, // 不解析未知属性
        parse_px_unit: false,
        skip_unresolved_classes: true,
        skip_invalid_attributes: true, // 跳过无效属性
        skip_invalid_css: true, // 跳过无效 CSS
        skip_paint_fallback: false,
    };

    // 定义清理选项（减少激进操作，保留渲染完整性）
    let clean_option = CleaningOptions {
        remove_unused_defs: true,
        convert_shapes: true, // 安全地将形状转换为路径
        remove_title: true,
        remove_desc: true,
        remove_metadata: true,
        remove_dupl_linear_gradients: true,
        remove_dupl_radial_gradients: true,
        remove_dupl_fe_gaussian_blur: true,
        ungroup_groups: false, // 保留组结构
        ungroup_defs: false, // 保留 defs 结构
        group_by_style: false,
        merge_gradients: false, // 避免合并渐变以防丢失
        regroup_gradient_stops: true,
        remove_invalid_stops: true,
        remove_invisible_elements: false, // 保留可能影响渲染的元素
        resolve_use: true,
        remove_version: true,
        remove_unreferenced_ids: true,
        trim_ids: true,
        remove_text_attributes: true,
        remove_unused_coordinates: true,
        remove_default_attributes: false, // 保留默认属性以防丢失样式
        remove_xmlns_xlink_attribute: false,
        remove_needless_attributes: false, // 避免移除可能必要的属性
        remove_gradient_attributes: false, // 保留渐变属性
        join_style_attributes: StyleJoinMode::None,
        apply_transform_to_gradients: false, // 避免对渐变应用变换
        apply_transform_to_shapes: true,
        paths_to_relative: true,
        remove_unused_segments: true,
        convert_segments: true,
        apply_transform_to_paths: true,
        coordinates_precision: 4, // 降低精度以减少浮点误差
        properties_precision: 4,
        paths_coordinates_precision: 6,
        transforms_precision: 6,
    };

    // 使用默认写入选项
    let write_option = WriteOptions::default();

    let mut buf = raw.to_owned().into_bytes();

    let mut doc = cleaner::parse_data(raw, &parse_option).unwrap();

    cleaner::clean_doc(&mut doc, &clean_option, &write_option).unwrap();

    buf.clear();

    cleaner::write_buffer(&doc, &write_option, &mut buf);

    String::from_utf8(buf).unwrap()
}
