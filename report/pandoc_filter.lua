
function Image(el)
    local path = string.sub(pandoc.utils.stringify(PANDOC_STATE.resource_path), 0, -2) .. "/" .. el.src
    local f = io.open(path, 'r')
    if f~=nil then
        io.close(f)
        return el
    else
        return el.caption
    end
end
