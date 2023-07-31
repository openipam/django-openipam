import { FilterFn, SortingFn } from "@tanstack/react-table";
import { rankItem } from "@tanstack/match-sorter-utils";

export const fuzzyFilter: FilterFn<any> = (row, columnId, value, addMeta) => {
  // Rank the item
  const itemRank = rankItem(row.getValue(columnId), value);

  // Store the itemRank info
  addMeta({
    itemRank,
  });

  // Return if the item should be filtered in/out
  return itemRank.passed;
};

export const stringFilter: FilterFn<any> = (
  row,
  columnId,
  filterValue,
  addMeta
) => {
  // Rank the item
  const v = row.getValue(columnId) as string | undefined;
  // test to see if v is included in value
  const passed =
    !filterValue ||
    (!!v && v.toLowerCase().includes(filterValue.toLowerCase()));

  const rank = {
    passed,
    rank: passed ? (1 as 1) : (0 as 0),
    rankedValue: v,
    accessorIndex: 1 as 1,
    accessorThreshold: 0 as 0,
  };
  // Store the itemRank info
  addMeta({
    itemRank: rank,
  });
  return passed;
};

export const betweenDatesFilter: FilterFn<any> = (
  row,
  columnId,
  filterValue,
  addMeta
) => {
  // given a date range, return true if the row's date is within the range
  const [min, max] = filterValue;
  const date = row.getValue(columnId) as any;
  if (!min && !max) {
    // passes
    const rank = {
      passed: true,
      rank: 1 as 1,
      rankedValue: date,
      accessorIndex: 1 as 1,
      accessorThreshold: 0 as 0,
    };
    addMeta({
      itemRank: rank,
    });
    return rank.passed;
  }
  if (!date) {
    console.log("date is undefined", row);
    // fails
    const rank = {
      passed: false,
      rank: 0 as 0,
      rankedValue: date,
      accessorIndex: 1 as 1,
      accessorThreshold: 0 as 0,
    };
    addMeta({
      itemRank: rank,
    });
    return rank.passed;
  }
  const dateValue = new Date(date).valueOf();
  const minDateValue = min ? new Date(min).valueOf() : 0;
  const maxDateValue = max ? new Date(max).valueOf() : Infinity;

  const passed = dateValue >= minDateValue && dateValue <= maxDateValue;
  console.log("betweenDatesFilter", {
    date,
    min,
    max,
    dateValue,
    minDateValue,
    maxDateValue,
    passed,
  });
  const rank = {
    passed,
    rank: passed ? (1 as 1) : (0 as 0),
    rankedValue: date,
    accessorIndex: 1 as 1,
    accessorThreshold: 0 as 0,
  };
  addMeta({
    itemRank: rank,
  });
  return passed;
};
