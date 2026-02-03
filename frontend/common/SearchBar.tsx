import { Artist } from "@/api-codegen/client";
type SearchBarProps = {
  placeholder: string;
  onSelect: (value: Artist) => void;
  searchValue: string;
  results: Artist[];
  handleSearch: (value: string) => void;
};
export default function SearchBar({
  placeholder,
  onSelect,
  searchValue,
  results,
  handleSearch,
}: SearchBarProps) {
  return (
    <div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (results.length > 0) {
            onSelect(results[0]);
          }
        }}
      >
        <input
          type="text"
          autoFocus
          id="name"
          placeholder={placeholder}
          className="text-5xl outline-none font-medium field-sizing-content pr-12"
          autoComplete="off"
          value={searchValue}
          onChange={(e) => {
            handleSearch(e.target.value);
          }}
        />
      </form>
      <div className="absolute w-128">
        {results.map((value) => {
          return (
            <div
              className="cursor-pointer"
              key={value.id}
              onClick={() => {
                onSelect(value);
              }}
            >
              {value.name}
            </div>
          );
        })}
      </div>
    </div>
  );
}
