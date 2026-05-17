import { FiChevronRight } from "react-icons/fi";

export default function Breadcrumbs({
  category = "Алгебра",
  current = "Упростить выражение",
}) {
  return (
    <div className="breadcrumbs">
      <span>Главная</span>
      <FiChevronRight />
      <span>{category}</span>
      <FiChevronRight />
      <span className="current">{current}</span>
    </div>
  );
}
