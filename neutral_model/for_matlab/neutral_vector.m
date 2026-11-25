function v = neutral_vector(el, keys)
%NEUTRAL_VECTOR Read numeric attributes of an XML element in the given order.
%   MATLAB version of vector in common/neutral_scene.py.

    v = cellfun(@(k) str2double(char(el.getAttribute(k))), keys);
end
